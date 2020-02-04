#-------------------AWS MQTT init----------------------
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


#----------------Global Variables----------------------------
Message = ''
TIMER = 0
Wflag = 0

mqtt_url = "a3hf64x6hul7tx-ats.iot.us-west-2.amazonaws.com"
root_ca = '/home/root/certs/Amazon_Root_CA_1.pem'
public_crt = '/home/root/certs/c17983007e-certificate.pem.crt'
private_key = '/home/root/certs/c17983007e-private.pem.key'


#----------------Functions-----------------------------------
def ledOn():
  os.system("echo 29 > /sys/class/gpio/export")
  os.system("echo out > /sys/class/gpio/PA29/direction")
  os.system("echo 1 > /sys/class/gpio/PA29/value")
  os.system("echo 29 > /sys/class/gpio/unexport")


def ledOff():
  os.system("echo 29 > /sys/class/gpio/export")
  os.system("echo out > /sys/class/gpio/PA29/direction")
  os.system("echo 0 > /sys/class/gpio/PA29/value")
  os.system("echo 29 > /sys/class/gpio/unexport")

def publishOn():
  client.publish("Aws_regor", '{"voltage":' + str(Volt_val) + ', "frequency":' + str(Freq_val) + ', "status": "ON", "kwh":' + str(kWh_val) + ', "cost":' + str(cost) + '}', qos = 1)

def publishOff():
  client.publish('Aws_regor', '{"voltage":' + str(Volt_val) + ', "frequency":' + str(Freq_val) + ', "status": "OFF", "kwh":' + str(kWh_val) + ', "cost":' + str(cost) + '}', qos = 1)
 

def timerCb():
  global Message
  global TIMER
  global Wflag
  print("Timer elapsed\n\nTurning off")
  #ledOff()
  publishOff()
  #client.publish('Aws_regor', '{"voltage":' +str(Volt_val)', "frequency":' +str(Freq_val)', "message": "OFF"}', qos = 1)
  Message = ''
  TIMER = 0
  Wflag = 0
  

def on_connect(client, userdata, flags, rc):
  print("Connected with result code " + str(rc))
  client.subscribe("ExampleTopic")
  print("Subscribed")


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

  if (Message == 'ON'):

      '''
                                                                                                       
      LineToNeutral = modclient.read_holding_registers(0x0F46, 2, unit=1)                                             
      decoder = BinaryPayloadDecoder.fromRegisters(LineToNeutral.registers, Endian.Big, wordorder=Endian.Little)
                                                                                                              
      Volt_val = float(decoder.decode_32bit_float())                                                                  
      print("Line To Neutral Voltage:", Volt_val)                                                                         
                                                                                                                    
      Frequency = modclient.read_holding_registers(0x0F4A, 2, unit=1)                                                    
      decoder = BinaryPayloadDecoder.fromRegisters(Frequency.registers, Endian.Big, wordorder=Endian.Little)          
                                                                                                                        
      Freq_val = float(decoder.decode_32bit_float())                                                               
      print("Frequency:", Freq_val)                                                                                                
      '''
      Freq_val = 49.906
      Volt_val = 230.507
      
      Watthour = modclient.read_holding_registers(0x009E, 2, unit=1)                                                
      decoder = BinaryPayloadDecoder.fromRegisters(Watthour.registers, Endian.Big, wordorder=Endian.Little)         
                                                                                                                         
      Wh_val = float(decoder.decode_32bit_float())
      kWh_val = Wh_val / 1000.0                                                                     
      print("kWh: ", kWh_val)

      if Wflag == 1:
        WhIn = Wh_val
        Wflag = 0

      print(WhIn, Wh_val, (Wh_val - WhIn))
      cost = (Wh_val - WhIn) * 0.2
                                                                                                                          
      print("==========================================================")                                        
                                                                                                               
                                                                                                                        
      #volt_val = str(LineToNeutral.registers)                                                                            
      #freq_val = str(Frequency.registers)                                                                                

      publishOn()                                                                                                                                                                                                                                                                      
      sleep(5)


  elif (Message == 'OFF'):
      
      Wflag = 0

  sleep(250/10000000.0)
