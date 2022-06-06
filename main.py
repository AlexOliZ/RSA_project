from flask import Flask, render_template
# from app import create_app
from flask_mqtt import Mqtt
import sys
import json
import threading
from paho.mqtt import client as mqtt_client
import time

topic = "vanetza/in/cam"
i = 1

app = Flask(__name__,
            template_folder='templates')

@app.route('/')
def index():
    # get obu's positions
    return render_template('index.html')

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
        # print("oi")
        payload=msg.payload.decode()
        json_rec = json.loads(payload)
        print("obu"+str(json_rec["stationID"]) +"lat="+str(json_rec["latitude"]), file=sys.stderr)
    client.subscribe(topic)
    client.on_message = on_message

def looping(client):
    while True:
        client.loop()
        # time.sleep(1)

for j in range(4):
    id = 'server_id'
    clientid = id+str(j)
    print('192.168.98.' + str(i*10), file=sys.stderr)
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



if __name__ == '__main__':
    app.run(debug=True)
    
