import docker


if __name__ == "__main__":
    client = docker.from_env()
    containers = client.containers.list()
    containers_info_list = []
    for container in containers:
        # print(container.stats(stream=False))
        # print(container.attrs)
        # containers_attrs_list.append(container.attrs)
        containers_info_list.append({
            'id': container.attrs['Id'],
            'attrs': container.attrs,
            'stats': container.stats(stream=False)
        })
