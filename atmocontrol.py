'''
Created on 20.05.2015

@author: mgolisch
'''
import paho.mqtt.client as mqtt
from xbmcjson import XBMC
import sh

xbmc_host = 'htpc'
xbmc_port=8081
xbmc_user='xbmc'
xbmc_password='xbmc'
mqtt_host='htpc'

#topics
atmo_mode_topic = '/openhab/atmo/mode'
atmo_color_topic = '/openhab/atmo/color'
atmo_constant_handle = None
atmo_color = 'FFFFFF'
atmo_mode = "0"

#xbmc boblight
def xbmc_boblight(enable):
    xbmc = XBMC('http://%s:%s/jsonrpc'%(xbmc_host,xbmc_port),xbmc_user,xbmc_password)
    xbmc.Addons.SetAddonEnabled({"addonid":"script.xbmc.boblight","enabled":enable})

def kill_constant():
    global atmo_constant_handle
    if atmo_constant_handle is not None:
            atmo_constant_handle.kill()
            atmo_constant_handle = None

def change_color(color):
    global atmo_color
    print color
    atmo_color = color
    if atmo_mode == "1":
        change_mode("1")

def change_mode(mode):
    #mode 0 = off
    #mode 1 = constant
    #mode 2 = xbmc
    global atmo_constant_handle,atmo_mode 
    if mode == "0" :
        kill_constant()
        xbmc_boblight(False)
    if mode == "1":
        kill_constant()
        xbmc_boblight(False)
        boblight_constant = sh.Command("/usr/local/bin/boblight-constant")
        atmo_constant_handle = boblight_constant(atmo_color,_bg=True,s=xbmc_host)
        
    
    if mode == "2":
        kill_constant()
        xbmc_boblight(True)
    atmo_mode = str(mode)
        
    

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(atmo_mode_topic)
    client.subscribe(atmo_color_topic)
    

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print msg.topic+" "+str(msg.payload)
    if msg.topic == atmo_mode_topic:
        if msg.payload not in ("0","1","2") :return
        change_mode(msg.payload)
    if msg.topic == atmo_color_topic:
        change_color(msg.payload)
        
            

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_host, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()