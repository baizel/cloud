#!/usr/bin/env python3.7
from pymongo import MongoClient

host = "ec2-54-159-99-219.compute-1.amazonaws.com"

client = MongoClient(host,
                     port=3306,
                     username='root',
                     password='toor',
                     authSource='admin',
                     authMechanism='SCRAM-SHA-256')
collections = client['recorded_stats'].list_collection_names()
for col in collections:
    print("Time,Cpu Usage, IO Time, Memory Usage")
    documents = list(client['recorded_stats'][col].find())
    for cont, row in enumerate(documents):
        # if cont != 0:
        #     print("{},{},{},{}".format(row["_id"],
        #                                    row["cpu_usage"] - documents[cont-1]["cpu_usage"],
        #                                    row["io_time"] - documents[cont-1]["io_time"],
        #                                    row["memory_usage"] - documents[cont-1]["memory_usage"]))
        #
            print("{},{},{},{}".format(row["_id"], row["cpu_usage"], row["io_time"], row["memory_usage"]))
