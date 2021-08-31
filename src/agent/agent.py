import time
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime
from typing import Any, List

import docker
import psutil
from loguru import logger
from requests import post

from .config import (
    BACKEND_ENDPOINT,
    HOME_PATH,
    HOST_ID,
    INFLUXDB_WRITE_INTERVAL_TIME,
    MAX_WORKERS,
)
from .dataclasses import BasicMetric, ContainerSummary, HostSummary


def get_metric_from_data(metric_name: str, data: Any) -> BasicMetric:
    if metric_name == "virtual_memory":
        return BasicMetric(data.used, data.total, data.percent)
    elif metric_name == "disk_memory":
        return BasicMetric(data.used, data.total, data.percent)
    elif metric_name == "host_cpu_usage":
        percentage = data
        return BasicMetric(percentage, 100, percentage)
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
        return BasicMetric(percentage, 100, percentage)
    elif metric_name == "container_memory_usage":
        return (
            BasicMetric(0, 0, 0)
            if not data
            else BasicMetric(
                data["usage"], data["limit"], (data["usage"] / data["limit"]) * 100
            )
        )
    else:
        logger.error(f"DID NOT FIND OPTION FOR {metric_name}")
        return None


class Agent:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    def get_containers_summary(self) -> List[ContainerSummary]:
        summaries = []
        containers_data = self.docker_client.containers.list(all=True)
        for c in containers_data:
            attrs, stats = c.attrs, c.stats(stream=False)
            memory_usage = get_metric_from_data(
                metric_name="container_memory_usage", data=stats["memory_stats"]
            )
            cpu_usage = get_metric_from_data(
                metric_name="container_cpu_usage", data=stats
            )
            container_summary = ContainerSummary(
                id=attrs["Id"],
                name=attrs["Name"],
                image=attrs["Config"]["Image"],
                status=attrs["State"]["Status"],
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
            )

            summaries.append(container_summary)
        return summaries

    def get_host_summary(self) -> HostSummary:
        virtual_memory_usage = get_metric_from_data(
            metric_name="virtual_memory", data=psutil.virtual_memory()
        )
        disk_memory_usage = get_metric_from_data(
            metric_name="disk_memory", data=psutil.disk_usage(HOME_PATH)
        )
        cpu_usage = get_metric_from_data(
            metric_name="host_cpu_usage", data=psutil.cpu_percent()
        )
        containers = self.get_containers_summary()
        timestamp = datetime.now()
        return HostSummary(
            timestamp, virtual_memory_usage, disk_memory_usage, cpu_usage, containers
        )

    def send_summary_to_backend(host_id: str, endpoint: str, data: Any) -> Any:
        url = endpoint + host_id
        response = post(url=url, data=data.to_json())
        print(response.json())

    def run(self):
        while True:
            host_summary = self.get_host_summary()
            self.send_summary_to_backend(
                host_id=HOST_ID, endpoint=BACKEND_ENDPOINT, data=host_summary
            )
            time.sleep(INFLUXDB_WRITE_INTERVAL_TIME)
