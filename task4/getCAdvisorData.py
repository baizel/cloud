import json
import time
import requests
import docker


def getCpuData(data):
    dataIndex = 0
    statsIndex = len(data[dataIndex]['stats']) - 1

    totalCpuUsage = data[dataIndex]['stats'][statsIndex]['cpu']['usage']['total']
    totalCpuUsagePrevious = data[dataIndex]['stats'][statsIndex - 1]['cpu']['usage']['total']
    timeStamp = data[dataIndex]['stats'][statsIndex]['timestamp'].split("T")[1].split(".")[0]
    diffInTime = (totalCpuUsage - totalCpuUsagePrevious) * 1e-9  # Nano seconds to seconds
    return timeStamp, diffInTime


def getMemoryData(data):
    dataIndex = 0
    statsIndex = len(data[dataIndex]['stats']) - 1
    timeStamp = data[dataIndex]['stats'][statsIndex]['timestamp'].split("T")[1].split(".")[0]
    memoryUsage = data[dataIndex]["stats"][statsIndex]["memory"]['usage'] * 1e-6  # bytes to MB
    return timeStamp, memoryUsage


def getIOTime(data):
    dataIndex = 0
    statsIndex = len(data[dataIndex]['stats']) - 1
    fileSystemIndex = len(data[dataIndex]['stats'][dataIndex]['filesystem']) - 1
    totalIOTime = data[dataIndex]['stats'][dataIndex]['filesystem'][fileSystemIndex]['io_time']
    timeStamp = data[dataIndex]['stats'][statsIndex]['timestamp'].split("T")[1].split(".")[0]
    return timeStamp, totalIOTime


if __name__ == "__main__":
    docker = docker.from_env()
    ids = []
    for i in docker.containers.list():
        if "java-app" in i.name:
            ids.append(i.id)
    instance1ContainerId = ids[0]
    instance2ContainerId = ids[1]
    url = "http://localhost:9090/api/v1.3/subcontainers/docker/{}".format(instance1ContainerId)
    url2 = "http://localhost:9090/api/v1.3/subcontainers/docker/{}".format(instance2ContainerId)

    urls = [url, url2]
    while True:
        for i in urls:
            data = json.loads(requests.get(url).content)
            timeStamp, cpuUsage = getCpuData(data)
            _, memoryUsage = getMemoryData(data)
            _, ioTime = getIOTime(data)
            print("Container id {:5s} Cpu usage: Time {}, Usage: {:.2f}s, Memory usage {} MB, I/O Time: {} ".format(i.split("docker/")[1][:5], timeStamp, cpuUsage, memoryUsage,ioTime))
        print("")
        time.sleep(1)
