'''
Created on 20.05.2015
Updated on 02.02.2021

@author: mgolisch
@editor: Marcel43367
'''
import paho.mqtt.client as mqtt
import subprocess
import time

##parameters
mqtt_host="melone"
device_name = "Boblight"
unique_id= "Boblight"
identifier= "a67hg458"
status_interval=60			#sec


#topics
command_topic = "homeassistant/light/boblight/light/switch"
state_topic = "homeassistant/light/boblight/light/status"
rgb_command_topic = "homeassistant/light/boblight/rgb/set"
rgb_state_topic = "homeassistant/light/boblight/rgb/status"
discovery_topic = "homeassistant/light/boblight/config"
availability_topic = "homeassistant/light/boblight/availability"

#global variables
atmo_color = "25,25,25"
atmo_mode = "OFF"

def kill_constant():
    subprocess.run(["killall","boblight-constant"])

def change_color(color):
    global atmo_color
    atmo_color = color
    
    if atmo_mode == "ON":
        change_mode("ON")

def change_mode(mode):
    #mode OFF = off
    #mode ON = constant
    global atmo_mode 
    if mode == "OFF" :
        kill_constant()
    if mode == "ON":
        kill_constant()
        
        # convert color to hex
        x = atmo_color.split(",", 3)
        colorHex = '{:02x}'.format(int(x[0]))+'{:02x}'.format(int(x[1]))+'{:02x}'.format(int(x[2]))
        
        # boblight-constant -o value=1 101010 -f -p 100
        subprocess.run(["boblight-constant","-o","value=" + "1 ",colorHex,"-f","-p","100"])
    atmo_mode = str(mode)
    

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(command_topic)
    client.subscribe(rgb_command_topic)
    
    device_msg = '"device": {"identifiers": ["' + identifier + '"],"name": "' + device_name + '", "model": "WS2801", "manufacturer": "Selfmade"}'
    
    pub_msg = '{"name": "' + device_name  + '", "unique_id": "' + unique_id + '", "availability_topic": "' + availability_topic + '", "state_topic": "' + state_topic + '", "command_topic": "' + command_topic + '", "rgb_state_topic": "' + rgb_state_topic + '", "rgb_command_topic": "' + rgb_command_topic + '", ' + device_msg + '}' 
    print(pub_msg)
   
    client.publish(discovery_topic,pub_msg,0,True)
    

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    msg.payload = msg.payload.decode("utf-8")
    print(msg.topic + " " + str(msg.payload))
    if msg.topic == command_topic:
        if msg.payload not in ("ON","OFF") :return
        change_mode(msg.payload)
    if msg.topic == rgb_command_topic:
        change_color(msg.payload)
    
    pub_status(client)	
 
# Status update to mqtt host
def pub_status(client):
    client.publish(state_topic, atmo_mode, 0, False)
    client.publish(rgb_state_topic, atmo_color, 0, False)
    client.publish(availability_topic, "online", 0, False)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.will_set(availability_topic, "offline", 0, True)

client.connect(mqtt_host, 1883, 60)

next_reading = time.time() 

client.loop_start()

try:
    while True:
        
        pub_status(client)

        next_reading += status_interval
        sleep_time = next_reading-time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
except KeyboardInterrupt:
    pass

client.loop_stop()
client.publish(availability_topic, "offline", 0, False)
client.disconnect()
