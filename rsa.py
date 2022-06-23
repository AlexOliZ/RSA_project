#!/usr/bin/python

from os import stat
from pydoc import cli
import threading
import random
import time
import json
import math
from random import shuffle as shuffle

from paho.mqtt import client as mqtt_client

import sys
from socket import socket, AF_INET, SOCK_DGRAM

port = 1883
topic_jetson = "jetson/demn"
topic_in = "vanetza/in/cam"
topic_out = "vanetza/out/cam"

speed_limit = 30 #m/s = 108km/h
count = 0
track = 1000 #m
theoric_dist = 10 #m

ip = "192.168.1.1"
PORT_NUMBER = 8080
SIZE = 1024

class OBUthread (threading.Thread):
    def __init__(self, threadID, name, delay, lat,obu_recv):
        threading.Thread.__init__(self)
        self.stationID = threadID
        self.name = name
        self.delay = delay
        self.brokerIp = '192.168.98.' + str(threadID*10)
        self.OBUinFront = obu_recv
        if(obu_recv == -1):
            self.leader = True
        else:
            self.leader = False
            self.leaderLat = -1
            self.leaderDist = -1
        self.Latitude = lat
        self.speed = 0
        self.started = False
        self.updateValues = False
        self.finishLat = lat - track*100
        self.finish = False
        # self.i = 0

    def run(self):
        print("Starting " + self.name)
        client = connect_mqtt(self.stationID,self.brokerIp)
        client.loop_start()
        t1 = threading.Thread(target=publish,args=(client,self.delay,self))
        t1.start()

        if self.leader:
            t2  = threading.Thread(target=listen_jetson,args=(client,self))
            t2.start()

        id = 'client_id'
        clientid = id+str(self.stationID)+str(self.stationID)
        client = connect_mqtt(clientid,self.brokerIp)   
        subscribe(client,self)
        client.loop_start()
     
        # print("Exiting " + self.name)

    def changeLocation(self,json):
        if(self.leader):

            if(self.Latitude < self.finishLat and self.speed > 0):
                self.speed -= 10
                self.Latitude -= (self.speed*self.delay)*100
            elif(self.Latitude < self.finishLat and self.speed < 1):
                self.finish = True
                print("FINISHED\n")
            elif(self.speed < speed_limit):
                self.speed += 3
                self.Latitude -= (self.speed*self.delay)*100

            else:
                self.Latitude -= (self.speed*self.delay)*100


            print("\nLEADER OBU"+str(self.stationID)+" with coordinates("+str(self.Latitude)+","+str(json["longitude"])+") + speed = "+str(self.speed))
        else:
            self.Latitude -= (self.speed*self.delay)*100

            self.leaderLat = json["latitude"]*10000000
            self.leaderDist = math.ceil((self.Latitude - self.leaderLat) / 100)
            delta = math.floor((self.leaderDist - theoric_dist))
            print("obu"+ str(self.stationID)+" dist from vehicle in front("+str(self.OBUinFront) +") = "+str(self.leaderDist)+"m")


            if(json["speed"] > self.speed and self.leaderDist > 0 and self.speed < 25):
                # self.speed += delta/self.delay + 2
                self.speed += 3 
            elif(self.leaderDist > 30 and self.speed >= 20 and self.speed < 35):
                self.speed += 5        
            elif(self.speed > 20 and self.leaderDist < 20):
                self.speed -= math.ceil(self.speed/5)

            
            # print("OBU"+str(self.stationID) +" received from "+str(json["stationID"])+ " speed= "+ str(json["speed"]))
            print("OBU"+str(self.stationID)+" received from "+str(json["stationID"])+" with coordinates("+str(self.Latitude)+","+str(json["longitude"])+") + speed = "+str(self.speed))
            # print("OBU"+str(self.stationID)+" received from "+str(json["stationID"])+" with coordinates("+str(json["latitude"])+","+str(json["longitude"])+")")

def listen_jetson(client,obu):
    listensocket = socket(AF_INET, SOCK_DGRAM)
    listensocket.bind((ip,PORT_NUMBER))
    while(1):
        (data,addr) = listensocket.recvfrom(SIZE)
        # generate demn
        x = {
            "management": {
                "actionID": {
                    "originatingStationID": 1,
                    "sequenceNumber": 0
                },
                "detectionTime": 1626453837.658,
                "referenceTime": 1626453837.658,
                "eventPosition": {
                    "latitude": obu.Latitude/10000000,
                    "longitude": -8.0810000,
                    "positionConfidenceEllipse": {
                        "semiMajorConfidence": 0,
                        "semiMinorConfidence": 0,
                        "semiMajorOrientation": 0
                    },
                    "altitude": {
                        "altitudeValue": 0,
                        "altitudeConfidence": 1
                    }
                },
                "validityDuration": 1,
                "stationType": 0
            },
            "situation": {
                "informationQuality": 7,
                "eventType": {
                    "causeCode": 14,
                    "subCauseCode": 14
                }
            }
        }
        # publish demn
        msg = json.dumps(x)
        # print(msg)
        result = client.publish(topic_in, msg)
        print(data,addr)

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

def publish(client,delay,obu):
    while True:
        time.sleep(delay)
        # print(obu.speed)
        # print(str(obu.stationID)+"this speed isssssss =>"+str(obu.speed))
        if(obu.finish == True):
            client.disconnect()
            break
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
            "heading": 3601,
            "headingConf": 127,
            "latitude": obu.Latitude/10000000,
            "length": 10.0,
            "longitude": -8.0810000,
            "semiMajorConf": 4095,
            "semiMajorOrient": 3601,
            "semiMinorConf": 4095,
            "specialVehicle": {
                "publicTransportContainer": {
                    "embarkationStatus": False
                }
            },
            "speed": obu.speed,
            "speedConf": 127,
            "speedLimiter": True,
            "stationID": obu.stationID,
            "stationType": 5,
            "width": 3.0,
            "yawRate": 0
        }

        msg = json.dumps(x)
        # print(msg)
        result = client.publish(topic_in, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            # print(f"Send msg to topic `{topic_in}`")
            a = 1
        else:
            print(f"Failed to send message to this topic {topic_in}")

def subscribe(client: mqtt_client,obu):
    def on_message(client, userdata, msg):
        global count

        m_decode = str(msg.payload.decode())
        m_json = json.loads(m_decode)
        # speed = m_json["speed"]

        if(m_json["stationID"] == obu.OBUinFront):
            obu.changeLocation(m_json)
        elif(obu.OBUinFront == -1 and count < 1):
            obu.changeLocation(m_json)
            count += 1
        elif(obu.OBUinFront == -1 and count >= 1):
            count += 1
        
        if count == 3:
            count = 0
            # print("reset")
        # print(speed)
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    client.subscribe(topic_out)
    client.on_message = on_message

def getLats():
    array = [1,2,3,4]
    shuffle(array)

    for x in range(4):
        array[x] = 376610000 + array[x]*1000

    my_dict = {}
    for x in range(4):
        my_dict[x] = array[x]
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

latitudes = getLats()
obus_sorted = sortDict(latitudes)

print(obus_sorted)

my_list = []
for x in range(4):
    temp_list = []
    last_element = 0

    for y in obus_sorted:
        if(x == y):
            break
        else:
            temp_list.append(y+1)

    if(temp_list != []):
        last_element = temp_list[-1]
    else:
        last_element = -1
    my_list.append(last_element)

# Create new threads
freq_sending = 1
thread1 = OBUthread(1, "OBU-1", freq_sending, latitudes[0], my_list[0])
thread2 = OBUthread(2, "OBU-2", freq_sending, latitudes[1], my_list[1])
thread3 = OBUthread(3, "OBU-3", freq_sending, latitudes[2], my_list[2])
thread4 = OBUthread(4, "OBU-4", freq_sending, latitudes[3], my_list[3])

# # Start new Threads
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()

# print("Exiting Main Thread")