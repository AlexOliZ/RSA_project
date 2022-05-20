#!/usr/bin/python

from os import stat
from pydoc import cli
import threading
import random
import time
import json

from paho.mqtt import client as mqtt_client

port = 1883
topic_in = "vanetza/in/cam"
topic_out = "vanetza/out/cam"



class myThread (threading.Thread):
    def __init__(self, threadID, name, delay, lat,obu_recv):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay
        self.brokerIp = '192.168.98.' + str(threadID*10)
        self.OBUinFront = obu_recv
        if(obu_recv == -1):
            self.leader = True
        else:
            self.leader = False
            self.leaderSpeed = 0
        self.Latitude = lat
        self.speed = 0
        self.started = False
        self.updateValues = False

    def get_speed(self):
        return self.speed

    def run(self):
        print("Starting " + self.name)
        client = connect_mqtt(self.threadID,self.brokerIp)
        client.loop_start()
        t1 = threading.Thread(target=publish,args=(client,self.delay,self.threadID,self.Latitude,self.speed))
        t1.start()

        id = 'client_id'
        clientid = id+str(self.threadID)+str(self.threadID)
        client = connect_mqtt(clientid,self.brokerIp)   
        subscribe(client)
        client.loop_start()
     
        # print("Exiting " + self.name)

    def changeLocation(self,json):
        # self.speed = json["speed"]
        # print("id"+str(self.threadID)+"speed="+str(self.speed))
        # print("id"+str(self.threadID)+"json:="+str(json["heading"]))

        if(self.leader):
            # print(self.threadID)
            if(self.started != True):
                print("Not Started")

                self.started = True
                self.speed += 2 #+2m/s
                self.Latitude += (self.speed*self.delay*10)
                # print(self.speed)
            else:
                print("Started")
                self.speed += 2 #+2m/s
                self.Latitude += (self.speed*self.delay*10)
                # print(self.speed)
        else:
            self.speed += json["speed"]
            self.Latitude += (self.speed*self.delay*10)
            print("OBU"+str(self.threadID)+" received from "+str(json["stationID"])+" with coordinates("+str(json["latitude"])+","+str(json["longitude"])+")")
    


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

def publish(client,delay,stationID,lat,speed):
    while True:
        time.sleep(delay)
        # if thread1.threadID == stationID:
        #     speed = thread1.speed
        #     lat = thread1.Latitude
        # elif thread2.threadID == stationID:
        #     speed = thread2.speed
        #     lat = thread2.Latitude
        # elif thread3.threadID == stationID:
        #     speed = thread3.speed
        #     lat = thread3.Latitude
        # elif thread4.threadID == stationID:
        #     speed = thread4.speed
        #     lat = thread4.Latitude

        # print(speed)
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
            "speed": speed*10,
            "speedConf": 127,
            "speedLimiter": True,
            "stationID": stationID,
            "stationType": 5,
            "width": 30,
            "yawRate": 0
        }
        msg = json.dumps(x)
        # print(msg)
        result = client.publish(topic_in, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send msg to topic `{topic_in}`")
        else:
            print(f"Failed to send message to this topic {topic_in}")
        # thread1.updateValues = False
        # thread2.updateValues = False
        # thread3.updateValues = False
        # thread4.updateValues = False

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        # global thread1
        m_decode = str(msg.payload.decode())
        m_json = json.loads(m_decode)
        speed = m_json["speed"]

        if(m_json["receiverID"] == 1):
            if(m_json["stationID"] == thread1.OBUinFront):
                thread1.changeLocation(m_json)
            elif(thread1.OBUinFront == -1):
                thread1.changeLocation(m_json)
                # thread1.updateValues = True
        elif(m_json["receiverID"] == 2):
            if(m_json["stationID"] == thread2.OBUinFront):
                thread2.changeLocation(m_json)
            elif(thread2.OBUinFront == -1):
                thread2.changeLocation(m_json)
                # thread2.updateValues = True
        elif(m_json["receiverID"] == 3):
            if(m_json["stationID"] == thread3.OBUinFront):
                thread3.changeLocation(m_json)
            elif(thread3.OBUinFront == -1):
                thread3.changeLocation(m_json)
                # thread3.updateValues = True
        elif(m_json["receiverID"] == 4):
            if(m_json["stationID"] == thread4.OBUinFront):
                thread4.changeLocation(m_json)
            elif(thread4.OBUinFront == -1):
                thread4.changeLocation(m_json)
                # thread4.updateValues = True
        # print(speed)
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    client.subscribe(topic_out)
    client.on_message = on_message

def getLats():
    my_dict = {}
    for x in range(4):
        my_dict[x] = random.randint(400000000,400001000)
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

# print(latitudes_sorted)

my_list = []
for x in range(4):
    temp_list = []
    last_element = 0

    for y in latitudes_sorted:
        if(x == y):
            break
        else:
            temp_list.append(y+1)

    if(temp_list != []):
        last_element = temp_list[-1]
    else:
        last_element = -1
    my_list.append(last_element)

# print(my_list)
# Create new threads
thread1 = myThread(1, "OBU-1", 0.2, latitudes_unsorted[0], my_list[0])
thread2 = myThread(2, "OBU-2", 0.2, latitudes_unsorted[1], my_list[1])
thread3 = myThread(3, "OBU-3", 0.2, latitudes_unsorted[2], my_list[2])
thread4 = myThread(4, "OBU-4", 0.2, latitudes_unsorted[3], my_list[3])

# # Start new Threads
thread1.start()
thread2.start()
thread3.start()
thread4.start()

# print("Exiting Main Thread")