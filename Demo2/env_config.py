#service port.
SERVICE_PORT = 6152
#DEBUG
IS_DEBUG = False

#db path.
DB_PATH = 'data/db'
#db config
DB_NAME = 'predictive_db'
#sensor data.
SENSOR_TABLE_NAME = 'sensor_details'
#sensor table column list.
SENSOR_COLUMNS = ['id', 'cycle', 'setting1', 'setting2', 'setting3', 's1', 's2', 's3', 's4', \
                   's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12', 's13', 's14', 's15',\
                   's16', 's17', 's18', 's19', 's20', 's21','createdt']

SENSOR_LIST = ['s1', 's2', 's3', 's4', \
                   's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12', 's13', 's14', 's15',\
                   's16', 's17', 's18', 's19', 's20', 's21']
#predict data
PREDICT_TABLE_NAME = 'predict_data'
#take top n records do predict
TOP_NUM = 6

##mqtt config###########
MQTT_BROKER = '10.75.161.193'
MQTT_PORT = 1883
MQTT_TOPIC = 'pm'
#mqtt connection keeplive
MQTT_KEEPLIVE = 60



