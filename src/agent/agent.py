import time
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, cast

import docker
import psutil
from decouple import config

from .common import get_iso_timestamp, get_metric_from_data, send_summary_to_backend
from .config import HOME_PATH, MAX_WORKERS
from .dataclasses import (
    BasicMetric,
    ContainerState,
    ContainerSummary,
    HostSummary,
    MetricType,
)


class Agent:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.prev_network_in_value = psutil.net_io_counters().bytes_recv
        self.prev_network_out_value = psutil.net_io_counters().bytes_sent

        self.host_id = config("HOST_ID", default="1")
        self.backend_endpoint = config(
            "BACKEND_ENDPOINT", default="http://localhost:8080/api/v2/metrics"
        )
        self.fetch_freq = config("FETCH_FREQ", default=10, cast=int)

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
                name=attrs["Name"],
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
            basic_metrics=[network_in, network_out],
            percent_metrics=[virtual_memory_metric, disk_memory_metric, cpu_metric],
            containers=containers,
        )

    def run(self):
        while True:
            host_summary = self.get_host_summary()
            send_summary_to_backend(endpoint=self.backend_endpoint, data=host_summary)
            time.sleep(self.fetch_freq)
