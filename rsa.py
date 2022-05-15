import random
import time
import json

from paho.mqtt import client as mqtt_client

i = '10'
broker = '192.168.98.'+i
port = 1883
topic = "vanetza/in/cam"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker,port)
    return client


def publish(client):
    while True:
        time.sleep(1)
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
            "stationID": 1,
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

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()