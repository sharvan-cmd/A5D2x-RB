#-------------------AWS MQTT init----------------------
import paho.mqtt.client as paho
import ssl, random
from time import sleep
import os
import json
import threading

mqtt_url = "a3hf64x6hul7tx-ats.iot.us-west-2.amazonaws.com"
root_ca = '/home/sharvan/certs/Amazon_Root_CA_1.pem'
public_crt = '/home/sharvan/certs/c17983007e-certificate.pem.crt'
private_key = '/home/sharvan/certs/c17983007e-private.pem.key'


#----------------Functions-----------------------------------
def publishOn():
  client.publish("Aws_regor", '{"voltage":' + str(Volt_val) + ', "frequency":' + str(Freq_val) + ', "status": "ON", "kwh":' + str(kWh_val) + ', "cost":' + str(cost) + '}', qos = 1)


def publishOff():
  client.publish('Aws_regor', '{"voltage":' + str(Volt_val) + ', "frequency":' + str(Freq_val) + ', "status": "OFF", "kwh":' + str(kWh_val) + ', "cost":' + str(cost) + '}', qos = 1)
 

def on_connect(client, userdata, flags, rc):
  print("Connected with result code " + str(rc))
  client.subscribe("ExampleTopic")
  print("Subscribed")

'''
def on_message(client, userdata, msg):
  global Message
  global TIMER
  global timer
  global Wflag
  print ("Message Received")
  print (msg.payload.decode("utf-8"))
  msg.payload=msg.payload.decode("utf-8")
  recvMesg = msg.payload
  jsonMesg = json.loads(recvMesg)
  Message = jsonMesg['message']
  if (Message == 'ON'):                             
    TIMER = jsonMesg['timer']
    timer = threading.Timer(TIMER * 60, timerCb)
    #ledOn()
    timer.start()
    Wflag = 1
    print("Turning on LED")
    #client.publish("sdk/test/cpp", 'ON', qos=1)

  elif (Message == 'OFF'):
    #ledOff()
    print ("Turning off LED")
    timer.cancel()
    publishOff()
    Wflag = 0
    #client.publish("sdk/test/cpp", 'OFF', qos=1)
'''

client = paho.Client()
client.tls_set(root_ca,
                   certfile = public_crt,
                   keyfile = private_key,
                   cert_reqs = ssl.CERT_REQUIRED,
                   tls_version = ssl.PROTOCOL_TLSv1_2,
                   ciphers = None)


client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_url, port = 8883, keepalive=60)
client.loop_start()                                                                                                      

while True:

    sleep(1)
