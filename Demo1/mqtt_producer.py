#! /usr/bin/env python
import pandas as pd
import json
import time
import paho.mqtt.client as mqtt

def main():
    #pass.
    client = mqtt.Client()
    client.connect("10.140.41.26",1883,60)
    topic = 'pm'
    
    while True:
        # read test data
        test_df = pd.read_csv('PM_test.txt', sep=" ", header=None)
        test_df.drop(test_df.columns[[26, 27]], axis=1, inplace=True)
        test_df.columns = ['id', 'cycle', 'setting1', 'setting2', 'setting3', 's1', 's2', 's3',
                     's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12', 's13', 's14',
                     's15', 's16', 's17', 's18', 's19', 's20', 's21']
        #json str to json object.
        json_arr = json.loads(test_df.to_json(orient='records'))

        index = 0
        for json_obj in json_arr:
            json_obj['ts'] = time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())
            #send to mqtt.
            print('sending message....{}'.format(json.dumps(json_obj)))
            client.publish(topic, json.dumps(json_obj))
            #sleep 5s
            time.sleep(3)
            index += 1

    #disconnect.
    client.disconnect()
        
main()
