"""
Agent setup.
"""
import docker_scraper
from datetime import datetime
import psutil
import yaml

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

with open('config.yaml', 'r') as config:
    cfg = yaml.load(config, Loader=yaml.BaseLoader)

INFLUXDB_ORGANIZATION = cfg['INFLUXDB_ORGANIZATION']
INFLUXDB_URL = cfg['INFLUXDB_URL']
INFLUXDB_BUCKET = cfg['INFLUXDB_BUCKET']
INFLUXDB_TOKEN = cfg['INFLUXDB_TOKEN']

if __name__ == "__main__":
    # containers_list = docker_scraper.get_containers_list()
    # print(containers_list)

    used_percent = psutil.virtual_memory().percent
    print(used_percent)

    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    point = Point("mem")\
        .tag("host", "my-host")\
        .field("used_percent", used_percent)\
        .time(datetime.utcnow(), WritePrecision.NS)

    write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORGANIZATION, point)




