"""
Scraping data form docker.
"""
import docker

client = docker.from_env()


def get_containers_list():
    containers = client.containers.list()
    containers_info_list = []
    for container in containers:
        containers_info_list.append({
            'id': container.attrs['Id'],
            'attrs': container.attrs,
            'stats': container.stats(stream=False)
        })

    print(containers_info_list)
