import csv
import time
from concurrent.futures.thread import ThreadPoolExecutor
import docker
import yaml
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
from datetime import datetime

from status_enum import Status

CONFIG_FILENAME = 'config.yaml'
MOCK_CONTAINERS_FILENAME = "container_stats.csv"
MAX_WORKERS = 50


class MockAgent:
    def __init__(self):
        try:
            self.configuration = self.get_configuration_from_yml()
            self.influxdb_client = InfluxDBClient(url=self.configuration['INFLUXDB_URL'],
                                                  token=self.configuration['INFLUXDB_TOKEN'])
            self.influxdb_write_options = ASYNCHRONOUS
            self.influxdb_data_writer = self.influxdb_client.write_api(self.influxdb_write_options)
            self.docker_client = docker.from_env()
            self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
            self.containers_info = self.get_containers_info_from_csv()
            self.total_virtual_memory = 4169125888
            self.total_disk_memory = 125910429696
            self.percent_virtual_memory = float("50")
            self.percent_disk_memory = float("50")
        except Exception as e:
            print(f"[ERROR] Configuration failed due to : {e}")
        else:
            print("Configuration successful")

    # returns configuration read from yml file
    def get_configuration_from_yml(self):
        with open(CONFIG_FILENAME, 'r') as config:
            return yaml.load(config, Loader=yaml.BaseLoader)

    def get_containers_info_from_csv(self):
        with open(MOCK_CONTAINERS_FILENAME, 'r') as data:
            containers = []
            for line in csv.DictReader(data):
                containers.append(line)

        return containers

    # saves point https://docs.influxdata.com/influxdb/v2.0/reference/glossary/#point to database
    def write_point_to_influxdb(self, point):
        try:
            self.influxdb_data_writer.write(self.configuration['INFLUXDB_BUCKET'],
                                            self.configuration['INFLUXDB_ORGANIZATION'],
                                            point)
        except Exception as e:
            print(f"Writing failed due to : {e}")
        else:
            pass

    # returns point from system statistics
    def create_point_from_system_data(self, total, name, percent):
        used = int(total * (percent / 100))
        return Point(name)\
            .time(datetime.utcnow(), WritePrecision.NS)\
            .field("total", total)\
            .field("used", used)\
            .field("percent", percent)

    # saves statistics about one container to influxdb
    def write_container_point_to_influx(self, container, name):
        container_stats_point = Point(name) \
            .time(datetime.utcnow(), WritePrecision.NS) \
            .tag("id", container['id']) \
            .tag("name", container['name']) \
            .tag('image', container['image']) \
            .field('status', int(container['status'])) \
            .field('memory_usage', int(container['memory_usage'])) \
            .field('cpu_percentage', float(container['cpu_percentage']))

        self.write_point_to_influxdb(container_stats_point)

    # saves statistics about all containers to influxdb
    def save_containers_stats_to_influx(self, name):
        for container in self.containers_info:
            self.executor.submit(self.write_container_point_to_influx, container, name)

    # saves statistics about host system to influxdb
    def save_host_stats_to_influx(self):
        virtual_memory_point = self.create_point_from_system_data(self.total_virtual_memory, "virtual_memory", self.percent_virtual_memory)
        disk_point = self.create_point_from_system_data(self.total_disk_memory, "disk", self.percent_disk_memory)

        self.write_point_to_influxdb(virtual_memory_point)
        self.write_point_to_influxdb(disk_point)

    def get_mock_stats_from_user(self):
        available_commands = 'Commands : disk | virtual | container | help'
        line = input("Enter command (or help to get commands) : ")

        if line == "help":
            print(available_commands)
        elif line == "disk":
            try:
                disk_percentage = float(input("Enter disk memory usage percentage (0 - 100): "))
                self.percent_disk_memory = disk_percentage
                print(f"Disk memory usage percentage set to : {disk_percentage} %")
            except Exception as e:
                print("Conversion failed")
        elif line == "virtual":
            try:
                virtual_percentage = float(input("Enter virtual memory usage percentage (0 - 100): "))
                self.percent_virtual_memory = virtual_percentage
                print(f"Virtual memory usage percentage set to : {virtual_percentage} %")
            except Exception as e:
                print("Conversion failed")
        elif line == "container":
            print("Available containers")
            for i in range(len(self.containers_info)):
                print(f"{i} : {self.containers_info[i]['name']} : {Status(int(self.containers_info[i]['status']))}")
            selected_container = int(input("Select container: "))

            if selected_container not in range(len(self.containers_info)):
                print("Invalid container")
            else:
                print("Available states")
                for status in Status:
                    print(f"{status.value} : {status.name}")
                selected_status = input("Select status: ")

                if int(selected_status) not in range(len(Status)):
                    print("Invalid status")
                else:
                    self.containers_info[selected_container]['status'] = selected_status
                    print(f"{self.containers_info[selected_container]['name']} changed status to {Status(int(selected_status))}")
        else:
            print("Incorrect command. Type help to get commands")

        self.get_mock_stats_from_user()

    # ongoing function to save all the info to influxdb every 'INFLUXDB_WRITE_INTERVAL_TIME' seconds
    def run(self):
        self.executor.submit(self.get_mock_stats_from_user)
        while True:
            #self.executor.submit(self.save_host_stats_to_influx)
            self.executor.submit(self.save_containers_stats_to_influx, "containers")
            time.sleep(int(self.configuration['INFLUXDB_WRITE_INTERVAL_TIME']))


