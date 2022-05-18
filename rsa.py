#!/usr/bin/python

import threading
import random
import time
import json

from paho.mqtt import client as mqtt_client

port = 1883
topic_in = "vanetza/in/cam"
topic_out = "vanetza/out/cam"


class myThread (threading.Thread):
    def __init__(self, threadID, name, delay, lat,obus_recv):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay
        self.brokerIp = '192.168.98.' + str(threadID*10)
        self.OBUSinFront = obus_recv
        self.initialLatitude = lat

    def run(self):
        print("Starting " + self.name)
        client = connect_mqtt(self.threadID,self.brokerIp)
        client.loop_start()
        # for obu in self.OBUSinFront:
        #
        t1 = threading.Thread(target=publish,args=(client,self.delay,self.threadID,self.initialLatitude))
        t1.start()
        # publish(client,self.delay,self.threadID,self.initialLatitude)
        print("Exiting " + self.name)

def connect_mqtt(id,broker):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(str(id))
    client.on_connect = on_connect
    client.connect(broker,port)
    return client

def publish(client,delay,stationID,lat):
    while True:
        time.sleep(delay)
        x = {
            "accEngaged": True,
            "acceleration": 0,
            "altitude": 800001,
            "altitudeConf": 15,
            "brakePedal": True,
            "collisionWarning": True,
            "cruiseControl": True,
            "curvature": 1023,
            "driveDirection": "FORWARD",
            "emergencyBrake": True,
            "gasPedal": False,
            "heading": 3601, #10¹
            "headingConf": 127,
            "latitude": lat, #10⁷
            "length": 100,
            "longitude": -80000000, #10⁷
            "semiMajorConf": 4095,
            "semiMajorOrient": 3601,
            "semiMinorConf": 4095,
            "specialVehicle": {
                "publicTransportContainer": {
                    "embarkationStatus": False
                }
            },
            "speed": 16383,
            "speedConf": 127,
            "speedLimiter": True,
            "stationID": stationID,
            "stationType": 5,
            "width": 30,
            "yawRate": 0
        }
        msg = json.dumps(x)
        print(msg)
        result = client.publish(topic_in, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send msg to topic `{topic_in}`")
        else:
            print(f"Failed to send message to this topic {topic_in}")

def getLats():
    my_dict = {}
    for x in range(4):
        my_dict[x] = random.randint(400000000,400010000)
    print(my_dict)
    return my_dict

def sortDict(dict):
    indexes = []

    sorted_values = sorted(dict.values()) # Sort the values
    sorted_dict = {}

    for i in sorted_values:
        for k in dict.keys():
            if dict[k] == i:
                sorted_dict[k] = dict[k]
                break

    for k in sorted_dict:
        indexes.append(k)

    return indexes

latitudes_unsorted = getLats()
latitudes_sorted = sortDict(latitudes_unsorted)

my_list = []
for x in range(4):
    temp_list = []
    for y in latitudes_sorted:
        if(x == y):
            break
        else:
            temp_list.append(y+1)
    my_list.append(temp_list)

# Create new threads
thread1 = myThread(1, "OBU-1", 10, latitudes_unsorted[0], my_list[0])
thread2 = myThread(2, "OBU-2", 10, latitudes_unsorted[1], my_list[1])
thread3 = myThread(3, "OBU-3", 10, latitudes_unsorted[2], my_list[2])
thread4 = myThread(4, "OBU-4", 10, latitudes_unsorted[3], my_list[3])

# Start new Threads
thread1.start()
thread2.start()
thread3.start()
thread4.start()

# print("Exiting Main Thread")