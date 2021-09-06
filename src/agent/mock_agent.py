import csv
import time
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from typing import List

from .common import send_summary_to_backend
from .config import (
    AVAILABLE_STATES,
    BACKEND_ENDPOINT,
    DISK_MEM_TOTAL,
    FETCH_FREQ,
    HOME_PATH,
    HOST_ID,
    MAX_WORKERS,
    MOCK_CONTAINERS_FILE,
    STARTING_PERCENT,
    VIRT_MEM_TOTAL,
)
from .dataclasses import BasicMetric, ContainerSummary, HostSummary


class MockAgent:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.total_virt_mem = VIRT_MEM_TOTAL
        self.total_disk_mem = DISK_MEM_TOTAL

        self.percent_virt_mem = STARTING_PERCENT
        self.percent_disk_mem = STARTING_PERCENT
        self.percent_cpu = STARTING_PERCENT / 10

        self.containers_info = self.get_containers_info_from_csv()

    def get_containers_info_from_csv(self):
        with MOCK_CONTAINERS_FILE.open() as f:
            containers = []
            for row in csv.DictReader(f):
                containers.append(row)
        return containers

    def set_host_param(self, line: str) -> None:
        try:
            percentage = float(input(f"Enter {line} usage percentage (0 - 100): "))
            if line == "disk mem":
                self.percent_disk_mem = percentage
            elif line == "virt mem":
                self.percent_virt_mem = percentage
            elif line == "cpu":
                self.percent_cpu = percentage
            print(f"{line} usage percentage set to : {percentage} %")
        except Exception:
            print("Conversion failed")

    def get_mock_stats_from_user(self):
        available_commands = "disk mem | virt mem | cpu | container"
        line = input(
            f"Available commands : {available_commands}\n Type in your command: "
        )

        if line in ["disk mem", "virt mem", "cpu"]:
            self.set_host_param(line)
        elif line == "container":
            print("Available containers")
            for i in range(len(self.containers_info)):
                print(
                    f"{i} : {self.containers_info[i]['name']} : {self.containers_info[i]['status']}"
                )
            selected_container = int(input("Select container: "))

            if selected_container not in range(len(self.containers_info)):
                print("Invalid container")
            else:
                print(f"Available states : {AVAILABLE_STATES}")
                selected_status = input("Type status: ")

                if selected_status not in AVAILABLE_STATES:
                    print("Invalid status")
                else:
                    self.containers_info[selected_container]["status"] = selected_status
                    print(
                        f"{self.containers_info[selected_container]['name']} changed status to {selected_status}"
                    )
        else:
            print("Incorrect command")

        self.get_mock_stats_from_user()

    def get_containers_summary(self) -> List[ContainerSummary]:
        summaries = []
        for container_info in self.containers_info:
            container_summary = ContainerSummary(
                id=container_info["id"],
                name=container_info["name"],
                image=container_info["image"],
                status=container_info["status"],
                memory_usage=container_info["memory_usage"],
                cpu_usage=container_info["cpu_usage"],
            )

            summaries.append(container_summary)
        return summaries

    def get_host_summary(self) -> HostSummary:
        virtual_memory_usage = BasicMetric(
            self.total_virt_mem * self.percent_virt_mem / 100,
            self.total_virt_mem,
            self.percent_virt_mem,
        )
        disk_memory_usage = BasicMetric(
            self.total_disk_mem * self.percent_disk_mem / 100,
            self.total_disk_mem,
            self.percent_disk_mem,
        )
        cpu_usage = BasicMetric(self.percent_cpu, 100, self.percent_cpu)
        containers = self.get_containers_summary()
        timestamp = datetime.now()
        return HostSummary(
            timestamp, virtual_memory_usage, disk_memory_usage, cpu_usage, containers
        )

    def send_summary(self) -> None:
        while True:
            host_summary = self.get_host_summary()
            send_summary_to_backend(
                host_id=HOST_ID, endpoint=BACKEND_ENDPOINT, data=host_summary
            )
            time.sleep(FETCH_FREQ)

    def run(self):
        self.executor.submit(self.get_mock_stats_from_user)
        self.executor.submit(self.send_summary)
