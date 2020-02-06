#-------------------AWSMQTTinit----------------------
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import paho.mqtt.client as paho
import ssl, random
from time import sleep
import os
import json
import threading

#-----------------MODBUS init---------------------------
from pymodbus.client.sync import ModbusSerialClient as ModbusClient                                                     
from pymodbus.payload import BinaryPayloadDecoder                                                                       
from pymodbus.payload import BinaryPayloadBuilder                                                                   
from pymodbus.constants import Endian                                                                                   
                                                                                                                    

#----------------Modbus client connection-------------------                                                                                                                        
modclient = ModbusClient(method='rtu', port='/dev/ttyS2', stopbits=1, bytesize=8, baudrate=9600, parity='N')               
connection = modclient.connect() 

counter = 1 

# AWS IoT certificate based connection

mqtt_url = "a3hf64x6hul7tx-ats.iot.us-west-2.amazonaws.com"
root_ca = '/home/root/certs/Amazon_Root_CA_1.pem'
public_crt = '/home/root/certs/c17983007e-certificate.pem.crt'
private_key = '/home/root/certs/c17983007e-private.pem.key'

def on_connect(client, userdata, flags, rc):
  print("Connected with result code " + str(rc))
  client.subscribe("ExampleTopic")
  print("Subscribed")


def on_message(client, userdata, msg):
  print ("Message Received")
  print (msg.payload.decode("utf-8"))
  msg.payload=msg.payload.decode("utf-8")
  recvMesg = msg.payload


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

                                                                

# Publish to the same topic in a loop forever                                                                           
loopCount = 0                                                                                                       
while True:         

    Watthour = modclient.read_holding_registers(0x009E, 2, unit=1)                                                
    decoder = BinaryPayloadDecoder.fromRegisters(Watthour.registers, Endian.Big, wordorder=Endian.Little) 

    Wh_val = float(decoder.decode_32bit_float())
    print("WattHour:",Wh_val)

    counter += 1

    client.publish("Aws_regor", "Watthour = " + str(Wh_val) + " " + str(loopCount), 1)
    loopCount += 1                                                                                                                                                    
    sleep(5)                      

