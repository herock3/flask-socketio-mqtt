import paho.mqtt.client as mqtt

from common_func import *
from model_plugin import *
import pandas as pd
from pandas import DataFrame

class MqttClient(threading.Thread):
    '''mqtt mqtt_client to consume message.'''

    def __init__(self):
        threading.Thread.__init__(self)
        self.mqtt_client = mqtt.Client()
        self.mqtt_broker = os.environ.get('MQTT_BROKER', MQTT_BROKER)
        self.mqtt_port = int(os.environ.get('MQTT_PORT', MQTT_PORT))
        self.mqtt_topic = os.environ.get('MQTT_TOPIC', MQTT_TOPIC)
        self.predict_queue = Queue.Queue(maxsize = 100 )
        self.sensor_queue = Queue.Queue(maxsize = 100 )
        self.is_refresh = True

        LOG.info('mqtt broker:{}, port:{}, topic:{}'.format(self.mqtt_broker, self.mqtt_port, self.mqtt_topic))

    #to update status
    def stop_mqttclient(self):
        LOG.info('stop mqtt client for broker: {}, topic:{}'.format(self.mqtt_broker, self.mqtt_topic))
        try:
            self.mqtt_client.disconnect()
        except:
            pass
     
    #call back func.
    def on_message(self,client,userdata, message):
        try:
            msg = json.loads(str(message.payload))
            LOG.debug('*** mqtt client received message: {} '.format(msg))
            
            data_ = []
            for col in SENSOR_COLUMNS[:-1]:
                data_.append(msg[col])
            data_.append(time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()))
            #compare cycle value.
            max_cycle = get_max_cycle(msg['id'])
            #LOG.debug('***************** max cycle:{}, current cycle:{}'.format(max_cycle,msg['cycle']))
            if len(max_cycle) and max_cycle[0] > msg['cycle']:
                LOG.debug('clear table .................')
                clear_table(SENSOR_TABLE_NAME)
                clear_table(PREDICT_TABLE_NAME);
            #save message.
            save_resp = save_data([tuple(data_)])
            LOG.debug('save data, resp:{}'.format(save_resp))
            if not save_resp['isSuccess']:
                LOG.error('save data failed, {}'.format(save_resp['msg']))
                return
            #get top N records
            sensor_list = get_sensors_top(msg['id'])
            #LOG.debug('get top sensor list: {}'.format(sensor_list))
            #call predictive model.
            if len(sensor_list) >= TOP_NUM:
                df = DataFrame(sensor_list, columns=SENSOR_COLUMNS)
                predict_df = (df.drop(['createdt'], axis=1)).sort_values('cycle')

                global predict_model
                predict_rul = predict_model.predict(predict_df)
                LOG.debug('predict rul:{}'.format(predict_rul))

                predict_result = []
                predict_result.append(msg['id'])
                predict_result.append(msg['cycle'])
                predict_result.append(int(round(predict_rul)))
                #save predict result.
                save_predict(predict_result)

                #refresh result.
                if self.is_refresh:
                    predict_history = get_predict_history(msg['id'])
                    predict_msg = []
                    for _p in predict_history:
                        predict_msg.append(dict(zip(('eid','cycle','rul'), _p)))
                else:
                    predict_msg = [dict(zip(['eid','cycle','rul'], predict_result))]
                #predict_msg = json.dumps(dict(zip(['eid','cycle','rul'], predict_result)))
                self.predict_queue.put(json.dumps(predict_msg))
                #LOG.debug('<<predict>> putting predict msg to queue:{}'.format(predict_msg))

            #put sensor data to queue.
            msg_list = []
            edata = []
            for k in SENSOR_LIST:
                sdata = []
                if self.is_refresh and k in ['s3','s8','s9','s12','s14','s20']:
                    #get history data.
                     sensor_list = get_sensors_history(msg['id'],k)
                     for (eid, cycle, sval) in sensor_list:
                         sdata.append(dict([('cycle',cycle),('data',sval)]))
                else:
                    sdata.append(dict(cycle=msg['cycle'], data=msg[k]))
                edata.append(dict([('sid',k),('sdata',sdata)]))
            #LOG.debug('is_refresh:{} ========================== edata:{}'.format(self.is_refresh,edata))
            
            if 'sensor_list' in locals() and len(sensor_list) > 0:
                self.is_refresh = False
            #put to the msg list.
            msg_list.append(dict([('eid', msg['id']),('edata', edata)]))
            #put to queue.
            #LOG.debug('<<sensor>> putting sensor msg to queue:{}'.format(msg_list))
            self.sensor_queue.put(msg_list)
        except Exception as ex:
            LOG.error(str(ex))

    #on connect.
    def on_connect(self, client, userdata, flags, rc):
        self.mqtt_client.subscribe(self.mqtt_topic)

    #thread.
    def run(self):
        LOG.info('...mqtt thread for topic {} start.'.format(self.mqtt_topic))
        tel_resp = telnet_mqtt_server(self.mqtt_broker, self.mqtt_port)
        if not tel_resp['isSuccess']:
            LOG.error(tel_resp['msg'])
            return

        try:
            self.mqtt_client.on_message = self.on_message
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, MQTT_KEEPLIVE)
            #self.mqtt_client.enable_logger(LOG)
            self.mqtt_client.loop_forever()
        except Exception as ex:
            LOG.error(str(ex))
        finally:
            self.mqtt_client.disconnect()

