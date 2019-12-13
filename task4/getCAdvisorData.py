#!/usr/bin/env python3.7
import datetime
import json
import sys
import time

import docker
import requests
from pymongo import MongoClient, UpdateOne

DELAY_BETWEEN_CALLS: float = 30.0  # in seconds


def getTimeStamp(statsData):
    tme = statsData['timestamp']
    return datetime.datetime.fromisoformat(tme.strip("Z").split(".")[0])


def getCpuData(statsData):
    return statsData['cpu']['usage']['total']


def getMemoryData(statsData):
    return statsData["memory"]['usage']


def getIOTime(statsData):
    return statsData['diskio']["io_time"][-1]["stats"]["Count"]


def getCombinedData(rawData):
    ret = []
    for i in rawData[0]['stats']:
        ret.append({"_id": getTimeStamp(i), "cpu_usage": getCpuData(i), "memory_usage": getMemoryData(i), "io_time": getIOTime(i)})
    return ret


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
    containerUrls = {}
    for i in docker.containers.list():
        if "java-app" in i.name:
            containerUrls[i.id] = "http://localhost:9090/api/v1.3/subcontainers/docker/{}".format(i.id)

    while True:
        for containerId in containerUrls.keys():
            url = containerUrls[containerId]
            rawData = json.loads(requests.get(url).content)
            dbData = getCombinedData(rawData)
            if writeToDb:
                client = MongoClient(host,
                                     port=3306,
                                     username='root',
                                     password='toor',
                                     authSource='admin',
                                     authMechanism='SCRAM-SHA-256')
                database = client["recorded_stats"]
                collection = database[containerId[:5]]  # Only use the first 5 chars of the id as table name
                upserts = [UpdateOne({'_id': x['_id']}, {'$setOnInsert': x}, upsert=True) for x in dbData]
                collection.bulk_write(upserts)
            for i in dbData:
                print("Container id {} Time {}, Cpus Usage: {:.4f}s, Memory usage {:.2f} MB, I/O Time: {} ".
                      format(containerId[:5], i["_id"], i["cpu_usage"] * 1e-9, i["memory_usage"] * 1e-6, i["io_time"]))
            print("")
        time.sleep(DELAY_BETWEEN_CALLS)
