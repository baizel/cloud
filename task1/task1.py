import docker

ports = {"8080/tcp": "8080"}
client = docker.from_env()
image = client.images.pull("nclcloudcomputing/javabenchmarkapp")

for c in client.containers.list():
    print("Stopping container " + c.name)
    c.stop()
print("Running nclcloudcomputing/javabenchmarkapp mapping port to " + str(ports))
container = client.containers.run("nclcloudcomputing/javabenchmarkapp", ports=ports, publish_all_ports=True, detach=True)
print("Container run in detached mode, Container name - " + container.name)
