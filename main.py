"""
Agent setup.
"""
import yaml
import docker_scraper

HOST = None
BUCKET = None
ORG = None
TOKEN = None

if __name__ == "__main__":
    with open('config.yaml', 'r') as config:
        cfg = yaml.load(config, Loader=yaml.BaseLoader)

    HOST = cfg['host']
    BUCKET = cfg['bucket']
    ORG = cfg['organization']
    TOKEN = ['token']

    docker_scraper.get_containers_list()
