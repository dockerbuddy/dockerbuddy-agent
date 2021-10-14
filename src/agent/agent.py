import os
import time
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from typing import Any, List

import docker
import psutil

from .common import get_metric_from_data, send_summary_to_backend
from .config import FETCH_FREQ, HOME_PATH, MAX_WORKERS
from .dataclasses import ContainerSummary, HostSummary


class Agent:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

        self.host_id = os.environ["HOST_ID"]
        self.backend_endpoint = os.environ["BACKEND_ENDPOINT"]

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
            self.host_id,
            timestamp,
            virtual_memory_usage,
            disk_memory_usage,
            cpu_usage,
            containers,
        )

    def run(self):
        while True:
            host_summary = self.get_host_summary()
            send_summary_to_backend(endpoint=self.backend_endpoint, data=host_summary)
            time.sleep(FETCH_FREQ)
