from time import sleep

import docker
from docker import DockerClient
from docker.errors import APIError
from docker.models.services import ServiceCollection
from docker.types import EndpointSpec


def createJavaService(client: DockerClient) -> ServiceCollection:
    image = "nclcloudcomputing/javabenchmarkapp"
    kwargs = {
        "endpoint_spec": EndpointSpec(ports={80: (8080, "tcp")}),
        "name": "java-app"
    }
    service = client.services.create(image, **kwargs).scale(2)
    print("created java-app service with scale of 2")
    return service


def createSwarmVisualizerService(client: DockerClient) -> ServiceCollection:
    image = "dockersamples/visualizer"
    kwargs = {
        "name": "visualizer",
        "endpoint_spec": EndpointSpec(ports={88: (8080, "tcp", "host")}),
        "constraints": ["node.role == manager"],
        "mounts": ["/var/run/docker.sock:/var/run/docker.sock"]
    }
    service = client.services.create(image, **kwargs)
    print("created visualizer service")
    return service


def createMongoService(client: DockerClient) -> ServiceCollection:
    image = "mongo"
    kwargs = {
        "name": "monog-db",
        "endpoint_spec": EndpointSpec(ports={3306: 27017}),
    }
    service = client.services.create(image, **kwargs)
    print("created Mongo service")
    return service


if __name__ == "__main__":
    cl = docker.from_env()
    # Create Swarm if not already done so
    try:
        swarm = cl.swarm.init()
        print("Created swarm: " + swarm.__str__())
    except APIError as e:
        print("Swarm already running")

    isRemoved = False
    for i in cl.services.list():
        print("Removing service " + i.name)
        i.remove()
        isRemoved = True
    if isRemoved:
        print("Waiting 5s for service to finish removing")
        sleep(5)
    createJavaService(cl)
    createSwarmVisualizerService(cl)
    createMongoService(cl)
