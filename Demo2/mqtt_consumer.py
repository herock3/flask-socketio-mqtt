import paho.mqtt.client as mqtt
import time
import logging
logging.basicConfig(level=logging.DEBUG)

def on_message(client, userdata, msg):
        #print(msg.topic+" "+str(msg.payload))
    print(time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()))
    print("topic:" ,msg.topic+", message: "+str(msg.payload))

def on_connect(client, userdata, flags, rc):
    client.subscribe('pm')
    pass

def main():
    broker_address = "10.75.161.193"
    port = 1883
    client = mqtt.Client('mqtt-consumer') 
    #logger = logging.getLogger('mqttclient')
    #client.enable_logger(logger)
    client.on_message = on_message
    client.on_connect = on_connect
    print('connecting to broker.')
    client.connect(broker_address, port, 60)
    client.loop_forever()

main()
