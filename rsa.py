#!/usr/bin/python

import threading
import random
import time
import json

from paho.mqtt import client as mqtt_client
exitFlag = 0
port = 1883
topic = "vanetza/in/cam"

class myThread (threading.Thread):
    def __init__(self, threadID, name, delay):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay
        self.brokerIp = '192.168.98.' + str(threadID*10)
    def run(self):
        print("Starting " + self.name)
        client = connect_mqtt(self.threadID,self.brokerIp)
        client.loop_start()
        publish(client,self.delay,self.threadID)
        # print_time(self.name, 5, self.counter)
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

def publish(client,delay,stationID):
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
            "latitude": 400000000, #10⁷
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
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send msg to topic `{topic}`")
        else:
            print(f"Failed to send message to this topic {topic}")

# Create new threads
thread1 = myThread(1, "OBU-1", 10)
thread2 = myThread(2, "OBU-2", 10)
thread3 = myThread(3, "OBU-3", 10)
thread4 = myThread(4, "OBU-4", 10)

# Start new Threads
thread1.start()
thread2.start()
thread3.start()
thread4.start()

# print("Exiting Main Thread")