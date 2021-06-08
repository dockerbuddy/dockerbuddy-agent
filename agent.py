import time
import docker
import yaml
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
from datetime import datetime
import psutil

CONFIG_FILENAME = 'config.yaml'
HOME_PATH = '/'


class Agent:
    def __init__(self):
        try:
            self.configuration = self.get_configuration_from_yml()
            self.influxdb_client = InfluxDBClient(url=self.configuration['INFLUXDB_URL'],
                                                  token=self.configuration['INFLUXDB_TOKEN'])
            self.influxdb_write_options = ASYNCHRONOUS
            self.influxdb_data_writer = self.influxdb_client.write_api(self.influxdb_write_options)
            self.docker_client = docker.from_env()
        except Exception as e:
            print(f"Configuration failed due to : {e}")
        else:
            print("Configuration successful")


    def get_configuration_from_yml(self):
        with open(CONFIG_FILENAME, 'r') as config:
            return yaml.load(config, Loader=yaml.BaseLoader)

    def write_point_to_influxdb(self, point):
        try:
            self.influxdb_data_writer.write(self.configuration['INFLUXDB_BUCKET'],
                                            self.configuration['INFLUXDB_ORGANIZATION'],
                                            point)
        except Exception as e:
            print(f"Writing failed due to : {e}")
        else:
            print(f"successful write {point}")

    def create_point_from_system_data(self, data, name):
        return Point(name)\
            .time(datetime.utcnow(), WritePrecision.NS)\
            .field("total", data.total)\
            .field("used", data.used)\
            .field("percent", data.percent)

    def write_docker_containers_stats(self, name, all):
        containers = self.docker_client.containers.list(all=all)
        for container in containers:
            container_stats_point = Point(name)\
                .time(datetime.utcnow(), WritePrecision.NS)\
                .tag("id", container.attrs['Id'])\
                .tag("name", container.attrs['Name'])\
                .tag('image', container.attrs['Config']['Image'])\
                .tag('status', container.attrs['State']['Status'])\
                .field('memory_usage', int(container.stats(stream=False)['memory_stats']['usage']))\
                .field('cpu_percentage', self.calculate_cpu_percentage(container.stats(stream=False)))

            self.write_point_to_influxdb(container_stats_point)

    def calculate_cpu_percentage(self, stats):
        return abs(stats['cpu_stats']['cpu_usage']['total_usage'] -
                   stats['precpu_stats']['cpu_usage']['total_usage']) * 100 \
                         / 10 ** 9  # Nanoseconds in one second

    def run(self):
        while True:
            virtual_memory_point = self.create_point_from_system_data(psutil.virtual_memory(), "virtual_memory")
            disk_point = self.create_point_from_system_data(psutil.disk_usage(HOME_PATH), "disk")
            self.write_point_to_influxdb(virtual_memory_point)
            self.write_point_to_influxdb(disk_point)
            self.write_docker_containers_stats("containers", False)
            time.sleep(int(self.configuration['INFLUXDB_WRITE_INTERVAL_TIME']))
