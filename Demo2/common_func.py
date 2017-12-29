import json
import time
import sqlite3 as sqlite
import commands
import telnetlib
import Queue
import threading

from env_config import *
from log_config import *

#global mqttc.
global mqttc_dict
mqttc_dict = dict()

#to get db path.
def get_dbpath():
    db_path = os.path.join(os.getcwd(), DB_PATH, DB_NAME + '.db')
    return db_path

#to init data..
def init():
    #create db path.
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)

    LOG.info('init the db start...')
    # Create table
    scripts = '''CREATE TABLE if not exists {} \
                  (id integer, cycle integer, setting1 real, setting2 real, setting3 real, s1 real, s2 real, s3 real, s4 real, \
                   s5 real, s6 real, s7 real, s8 real, s9 real, s10 real, s11 real, s12 real, s13 real, s14 real, s15 real,\
                   s16 real, s17 real, s18 real, s19 real, s20 real, s21 real, createdt text);
                CREATE TABLE if not exists {} \
                    (id integer PRIMARY KEY AUTOINCREMENT, eid integer, cycle integer, rul real, createdt text);'''\
                .format(SENSOR_TABLE_NAME, PREDICT_TABLE_NAME)
    #run the cmd.
    execute_script(True, scripts)
    LOG.info('init the db complete...')


#to execute insert
'''
purchases = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
             ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
            ]
c.executemany('INSERT INTO stocks VALUES (?,?,?,?,?)', purchases)
'''
def insert_records(sql, row_list):
    #LOG.debug('insert records sql: %s, row list: %s', sql, row_list)
    resp = {}
    isSuccess = True
    msg = None
    try:
        with sqlite.connect(get_dbpath()) as conn:
            c = conn.cursor()
            c.executemany(sql, row_list)
            conn.commit()
    except sqlite.Error as ex:
        isSuccess = False
        msg = str(ex)
   
    resp['isSuccess'] = isSuccess
    resp['msg'] = msg

    LOG.debug('insert records resp: %s', json.dumps(resp))

    return resp

#get records from table.
def get_records(fetchOne, sql):
    #LOG.debug('fetchOne: {}, get records sql: {}'.format(fetchOne, sql))
    record_list = []
    try:
        with sqlite.connect(get_dbpath()) as conn:
            c = conn.cursor()
            c.execute(sql)
            record_list = c.fetchone() if fetchOne else c.fetchall()
    except sqlite.Error  as ex:
        LOG.error(str(ex))

    #LOG.debug('get records resp: %s', record_list)
    return record_list


#execute update.
def update_records(scripts):
    return execute_script(False, scripts)   

#update records.
def execute_script(isScript, scripts):
    LOG.debug('execute scripts: %s', scripts)
    resp = {}
    isSuccess = True
    msg = None
    try:
        with sqlite.connect(get_dbpath()) as conn:
            c = conn.cursor()
            if isScript:
                c.executescript(scripts)
            else:
                c.execute(scripts)
            conn.commit()
    except sqlite.Error as ex:
        isSuccess = False
        msg = str(ex)

    resp['isSuccess'] = isSuccess
    resp['msg'] = msg

    LOG.debug('execute scripts resp: %s', json.dumps(resp))
    return resp


'''save data to db'''
def save_data(datalist):
    save_sql = 'INSERT INTO {} ({}) VALUES ({})'.format(SENSOR_TABLE_NAME,','.join(SENSOR_COLUMNS), ('?,' * len(SENSOR_COLUMNS)).strip(','))

    #save.
    return insert_records(save_sql, datalist)
    

#get top sensor records.
def get_sensors_top(eid):
    list_sql = 'select {} from {} where id = {} order by cycle desc limit {} '.format(','.join(SENSOR_COLUMNS), SENSOR_TABLE_NAME, eid, TOP_NUM)

    #LOG.debug('get top sensor sql: {}'.format(list_sql))
 
    return get_records(False, list_sql)

#get history sensor data.
''' params:
    eid: engineid,
    sid: sensorid
 '''
def get_sensors_history(eid, sid):
    list_sql = 'select id, cycle, {} from {} where id = {} '.format(sid, SENSOR_TABLE_NAME, eid)

    LOG.debug('get sensor history sql: {}'.format(list_sql))

    return get_records(False, list_sql)


'''to clear table'''
def clear_table(tableName):
    clear_sql = 'delete from {}'.format(tableName)
    return update_records(clear_sql)

'''get max cycle'''
def get_max_cycle(eid):
    get_sql = 'select MAX(cycle) from {} where id = {}'.format(SENSOR_TABLE_NAME, eid)
    return get_records(True, get_sql)

#save predict data.
def save_predict(pdata):
    save_sql = 'INSERT INTO {} (eid, cycle, rul, createdt) VALUES (?,?,?,?)'.format(PREDICT_TABLE_NAME)
    
    pdata.append(time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()))
    #save.
    return insert_records(save_sql, [tuple(pdata)])

#get predict history.
def get_predict_history(eid):
    list_sql = 'select eid, cycle, rul from {} where eid = {} '.format(PREDICT_TABLE_NAME, eid)

    LOG.debug('get predict history sql: {}'.format(list_sql))

    return get_records(False, list_sql)

#run command.
def runCommand(cmd):
    LOG.debug('run command: %s', cmd)
    resp = commands.getstatusoutput(cmd)
    LOG.debug('run command resp: %s', resp) 

    return resp       


#telnet mqtt server.
def telnet_mqtt_server(broker_address, port=1883):
    LOG.info('telnet broker address {} at port {} '.format(broker_address, port))
    resp = {}
    isSuccess = True
    msg = None
    tn = telnetlib.Telnet()
    try:
        tn.open(broker_address, port, 2)
    except:
        isSuccess = False
        msg = 'failed to connect broker {} at port {}'.format(broker_address, port)
    finally:
        if not tn:
            tn.close()
    resp['isSuccess'] = isSuccess
    resp['msg'] = msg
    
    return resp

#to make response.
def makeResponse(msg, code):
    LOG.info(msg)
    return jsonify({'msg': msg ,'status': code})

