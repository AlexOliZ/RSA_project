from flask import Flask, render_template, Response
# from app import create_app
from flask_mqtt import Mqtt
import sys
import json
import threading
from paho.mqtt import client as mqtt_client
import time

topic = "vanetza/in/cam"
i = 1
lat1 = 37.6614
lat2 = 37.6613
lat3 = 37.6612
lat4 = 37.6611

app = Flask(__name__,
            template_folder='templates')


def connect_mqtt(id,broker):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!",file=sys.stderr)
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(str(id))
    client.on_connect = on_connect
    client.connect(broker,1883)
    return client

def subscribe(client):
    def on_message(client, userdata, msg):
        global lat1
        global lat2
        global lat3
        global lat4

        payload=msg.payload.decode()
        json_rec = json.loads(payload)
        # print("obu"+str(json_rec["stationID"]) +"lat="+str(json_rec["latitude"]), file=sys.stderr)
        stationID = json_rec["stationID"]
        lat = json_rec["latitude"]

        if(stationID == 1):
            lat1 = lat
        elif(stationID == 2):
            lat2 = lat
        elif(stationID == 3):
            lat3 = lat
        elif(stationID == 4):
            lat4 = lat
    client.subscribe(topic)
    client.on_message = on_message

def looping(client):
    while True:
        client.loop()
        # time.sleep(1)

def generate_data():
    global lat1
    global lat2
    global lat3
    global lat4

    while True:
        json_data = json.dumps(
            {
                "obu1": lat1,
                "obu2": lat2,
                "obu3": lat3,
                "obu4": lat4,
            }
        )
        yield f"data:{json_data}\n\n"
        time.sleep(0.1)

for j in range(4):
    id = 'server_id'
    clientid = id+str(j)
    # print('192.168.98.' + str(i*10), file=sys.stderr)
    client = connect_mqtt(clientid,'192.168.98.' + str(i*10))   
    subscribe(client)
    if i == 1:
        t1 = threading.Thread(target=looping,args=(client,))
        t1.start()
    elif i == 2:
        t2 = threading.Thread(target=looping,args=(client,))
        t2.start()
    if i == 3:
        t3 = threading.Thread(target=looping,args=(client,))
        t3.start()
    if i == 4:
        t4 = threading.Thread(target=looping,args=(client,))
        t4.start()
    
    # client.loop_start()
    i+=1

@app.route('/')
def index():
    # get obu's positions
    return render_template('index.html')

@app.route("/realtimedata")
def obusdata():
    return Response(generate_data(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True)
    
