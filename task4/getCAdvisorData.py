import json
import time
import requests
import docker
import sys
from pymongo import MongoClient


def stripTime(tme):
    return tme.split("T")[1].split(".")[0]


def getCpuData(data):
    dataIndex = 0
    statsIndex = len(data[dataIndex]['stats']) - 1

    totalCpuUsage = data[dataIndex]['stats'][statsIndex]['cpu']['usage']['total']
    totalCpuUsagePrevious = data[dataIndex]['stats'][statsIndex - 1]['cpu']['usage']['total']
    timeStamp = data[dataIndex]['stats'][statsIndex]['timestamp']
    diffInTime = (totalCpuUsage - totalCpuUsagePrevious) * 1e-9  # Nano seconds to seconds
    return timeStamp, diffInTime


def getMemoryData(data):
    dataIndex = 0
    statsIndex = len(data[dataIndex]['stats']) - 1
    timeStamp = data[dataIndex]['stats'][statsIndex]['timestamp']
    memoryUsage = data[dataIndex]["stats"][statsIndex]["memory"]['usage'] * 1e-6  # bytes to MB
    return timeStamp, memoryUsage


def getIOTime(data):
    dataIndex = 0
    statsIndex = len(data[dataIndex]['stats']) - 1
    totalIOTime = data[dataIndex]['stats'][statsIndex]['diskio']["io_time"][-1]["stats"]["Count"]  # -1 for the last one in list
    timeStamp = data[dataIndex]['stats'][statsIndex]['timestamp']
    return timeStamp, totalIOTime


if __name__ == "__main__":
    writeToDb = False
    host = None
    if len(sys.argv) > 1 and sys.argv[1] == "-r":
        if len(sys.argv) > 2 and sys.argv[2] is not None:
            print("Data will be recorded to database")
            host = sys.argv[2]
            writeToDb = True

        else:
            raise ValueError("no host provided for database")

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
            id = i.split("docker/")[1]
            data = json.loads(requests.get(url).content)
            timeStamp, cpuUsage = getCpuData(data)
            _, memoryUsage = getMemoryData(data)
            _, ioTime = getIOTime(data)
            print("Container id {} Cpu usage: Time {}, Usage: {:.4f}s, Memory usage {} MB, I/O Time: {} ".format(id[:5], stripTime(timeStamp), cpuUsage, memoryUsage, ioTime))
            if writeToDb:
                client = MongoClient(host,
                                     port=3306,
                                     username='root',
                                     password='toor',
                                     authSource='admin',
                                     authMechanism='SCRAM-SHA-256')
                database = client["recorded_stats"]
                collection = database["data"]
                dataForDb = {"containerId": id, "timestamp": timeStamp, "cpu_usage": cpuUsage, "memory_usage": memoryUsage, "io_time": ioTime}
                collection.insert_one(dataForDb)
        print("")
        time.sleep(3)
