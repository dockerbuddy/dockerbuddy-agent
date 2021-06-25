import time
from concurrent.futures.thread import ThreadPoolExecutor
import docker
import yaml
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
from datetime import datetime

CONFIG_FILENAME = 'config.yaml'
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

    # calculate cpu percentage
    def calculate_cpu_percentage(self, stats):
        return abs(stats['cpu_stats']['cpu_usage']['total_usage'] -
                   stats['precpu_stats']['cpu_usage']['total_usage']) * 100 \
               / 10 ** 9  # Nanoseconds in one second

    # saves statistics about one container to influxdb
    def write_container_point_to_influx(self, container, name):
        attrs, stats = container.attrs, container.stats(stream=False)
        container_stats_point = Point(name) \
            .time(datetime.utcnow(), WritePrecision.NS) \
            .field("id", attrs['Id']) \
            .field("name", attrs['Name']) \
            .field('image', attrs['Config']['Image']) \
            .field('status', attrs['State']['Status']) \
            .field('memory_usage', int(stats['memory_stats']['usage'])) \
            .field('cpu_percentage', self.calculate_cpu_percentage(stats))

        self.write_point_to_influxdb(container_stats_point)

    # saves statistics about all containers to influxdb
    def save_containers_stats_to_influx(self, name, all):
        containers = self.docker_client.containers.list(all=all)

        for container in containers:
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
        else:
            print("Incorrect command. Type help to get commands")

        self.get_mock_stats_from_user()

    # ongoing function to save all the info to influxdb every 'INFLUXDB_WRITE_INTERVAL_TIME' seconds
    def run(self):
        self.executor.submit(self.get_mock_stats_from_user)
        while True:
            self.executor.submit(self.save_host_stats_to_influx)
            #self.executor.submit(self.save_containers_stats_to_influx, "containers", False)
            time.sleep(int(self.configuration['INFLUXDB_WRITE_INTERVAL_TIME']))