import enum
import os
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, List

import docker
import psutil
from dataclasses_json import LetterCase, dataclass_json
from loguru import logger
from requests.api import post

HOME_PATH = "/"
MAX_WORKERS = 50
CHECK_IF_AGENT_ALIVE_TIME = 10


class ContainerState(enum.Enum):
    restarting = "RESTARTING"
    dead = "DEAD"
    created = "CREATED"
    exited = "EXITED"
    paused = "PAUSED"
    running = "RUNNING"
    removing = "REMOVING"


class MetricType(enum.Enum):
    memory_usage = "MEMORY_USAGE"
    disk_usage = "DISK_USAGE"
    cpu_usage = "CPU_USAGE"
    network_in = "NETWORK_IN"
    network_out = "NETWORK_OUT"


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BasicMetric:
    metric_type: MetricType
    value: float


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PercentMetric:
    metric_type: MetricType
    value: float
    total: float
    percent: float


def get_container_name(container_name: str) -> str:
    if container_name.startswith("/"):
        return container_name[1:]
    return container_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ContainerSummary:
    id: str
    name: str
    image: str
    state: str
    metrics: List[PercentMetric]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class HostSummary:
    id: str
    timestamp: datetime
    sender_interval: int
    basic_metrics: List[BasicMetric]
    percent_metrics: List[PercentMetric]
    containers: List[ContainerSummary]


def send_summary_to_backend(endpoint: str, data: Any) -> None:
    try:
        headers = {"Content-type": "application/json", "Accept": "application/json"}
        response = post(url=endpoint, headers=headers, data=data.to_json())
        print(data.to_json())
        logger.info(f"SENT SUMMARY TO {endpoint}. STATUS CODE: {response.status_code}")
    except Exception as e:
        logger.error(f"FAILED TO SEND SUMMARY TO {endpoint}")


def get_metric_from_data(metric_name: str, data: Any) -> PercentMetric:
    if metric_name == "virtual_memory":
        return PercentMetric(
            MetricType.memory_usage, data.used, data.total, data.percent
        )
    elif metric_name == "disk_memory":
        return PercentMetric(MetricType.disk_usage, data.used, data.total, data.percent)
    elif metric_name == "host_cpu_usage":
        percentage = data
        return PercentMetric(MetricType.cpu_usage, percentage, 100, percentage)
    elif metric_name == "container_cpu_usage":
        # NOTE (@bplewnia) - Divide by number of nanoseconds in second -> 10e9
        percentage = (
            abs(
                data["cpu_stats"]["cpu_usage"]["total_usage"]
                - data["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            * 100
            / 10 ** 9
        )
        return PercentMetric(MetricType.cpu_usage, percentage, 100, percentage)
    elif metric_name == "container_memory_usage":
        return (
            PercentMetric(MetricType.memory_usage, 0, 0, 0)
            if not data
            else PercentMetric(
                MetricType.memory_usage,
                data["usage"],
                data["limit"],
                (data["usage"] / data["limit"]) * 100,
            )
        )
    else:
        logger.error(f"DID NOT FIND OPTION FOR {metric_name}")
        return PercentMetric(MetricType.cpu_usage, 0, 0, 0)


def get_iso_timestamp() -> str:
    return (
        datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None).isoformat() + "Z"
    )


class Agent:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.prev_network_in_value = psutil.net_io_counters().bytes_recv
        self.prev_network_out_value = psutil.net_io_counters().bytes_sent

        self.host_id = os.environ.get(
            "AGENT_HOST_ID", default="de87939b-d40d-4dba-85ee-04d0cdd6b5d4"
        )
        self.backend_endpoint = os.environ.get(
            "AGENT_BACKEND_ENDPOINT", default="http://localhost:8080/api/v2/metrics"
        )
        self.fetch_freq = int(os.environ.get("AGENT_FETCH_FREQ", default="10"))

    def get_network_metric(
        self, metric_name: str, data: int, prev_value: int
    ) -> BasicMetric:
        value = data - prev_value
        if metric_name == "network_in":
            self.prev_network_in_value = data
            return BasicMetric(MetricType.network_in, value)
        elif metric_name == "network_out":
            self.prev_network_out_value = data
            return BasicMetric(MetricType.network_out, value)
        else:
            pass

    def get_containers_summary(self) -> List[ContainerSummary]:
        summaries = []
        containers_data = self.docker_client.containers.list(all=True)
        for c in containers_data:
            attrs, stats = c.attrs, c.stats(stream=False)
            virtual_memory_metric = get_metric_from_data(
                metric_name="container_memory_usage", data=stats["memory_stats"]
            )
            cpu_metric = get_metric_from_data(
                metric_name="container_cpu_usage", data=stats
            )
            container_summary = ContainerSummary(
                id=attrs["Id"],
                name=get_container_name(attrs["Name"]),
                image=attrs["Config"]["Image"],
                state=ContainerState[attrs["State"]["Status"]].name,
                metrics=[virtual_memory_metric, cpu_metric],
            )

            summaries.append(container_summary)
        return summaries

    def get_host_summary(self) -> HostSummary:
        virtual_memory_metric = get_metric_from_data(
            metric_name="virtual_memory", data=psutil.virtual_memory()
        )
        disk_memory_metric = get_metric_from_data(
            metric_name="disk_memory", data=psutil.disk_usage(HOME_PATH)
        )
        cpu_metric = get_metric_from_data(
            metric_name="host_cpu_usage", data=psutil.cpu_percent()
        )
        network_in = self.get_network_metric(
            metric_name="network_in",
            data=psutil.net_io_counters().bytes_recv,
            prev_value=self.prev_network_in_value,
        )
        network_out = self.get_network_metric(
            metric_name="network_out",
            data=psutil.net_io_counters().bytes_sent,
            prev_value=self.prev_network_out_value,
        )
        containers = self.get_containers_summary()
        return HostSummary(
            id=self.host_id,
            timestamp=get_iso_timestamp(),
            sender_interval=self.fetch_freq,
            basic_metrics=[network_in, network_out],
            percent_metrics=[virtual_memory_metric, disk_memory_metric, cpu_metric],
            containers=containers,
        )

    def run(self):
        while True:
            host_summary = self.get_host_summary()
            send_summary_to_backend(endpoint=self.backend_endpoint, data=host_summary)
            time.sleep(self.fetch_freq)


if __name__ == "__main__":
    agent_thread = threading.Thread(target=Agent().run, daemon=True)
    agent_thread.start()

    while True:
        time.sleep(CHECK_IF_AGENT_ALIVE_TIME)
        if not agent_thread.is_alive():
            agent_thread = threading.Thread(target=Agent().run, daemon=True)
            agent_thread.start()
