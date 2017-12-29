#! /usr/bin/env python

"""flask service"""
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit

from common_func import *
from  mqtt_client import *

import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.secret_key = 'flask_secret'

#socket io.
socketio = SocketIO(app)
#cross domain.
CORS(app)

global socket_sender_predict_running
socket_sender_predict_running = False

global socket_sender_thread_running
socket_sender_thread_running = False

@app.route('/')
def index_page():
    return render_template('index.html')

#ws for mqtt connect.
@socketio.on('on_connect', namespace='/socket')
def socket_connect():
    LOG.info('>>>>>> web socket connectted.')
    #start mqtt client.
    global mqttc_dict
    if not len(mqttc_dict):
        mqttc = MqttClient()
        mqttc.start()
        mqttc_dict[1] = mqttc
    else:
        mqttc_dict[1].is_refresh = True

#send predict message.
@socketio.on('on_message_predict', namespace='/socket')
def message_predict():
    LOG.info('>>>>>> web socket predict message connected.')
    global mqttc_dict
    global socket_sender_predict_running
    if len(mqttc_dict) > 0 and not socket_sender_predict_running:
        st = SocketSender(socketio, True, mqttc_dict[1].predict_queue)
        st.start()
        socket_sender_predict_running = True

#send sensor message.    
@socketio.on('on_message_sensor', namespace='/socket')
def message_sensor(message):
    LOG.info('>>>>>> web socket sensor message connected.')
    ##check if need to update sid dict.
    global socket_sender_thread_running
    if not socket_sender_thread_running:
        global mqttc_dict
        sst = SocketSender(socketio, False ,mqttc_dict[1].sensor_queue)
        sst.start()
        socket_sender_thread_running = True

#disconnect websocket.
@socketio.on('on_disconnect', namespace='/socket')
def socket_disconnect():
    LOG.info('>>>>>> web socket disconnected.')
    #stop mqtt client.
    global mqttc_dict
    if len(mqttc_dict):
        mqttc_dict.pop(1).stop_mqttclient()
        global socket_sender_thread_running
        socket_sender_thread_running = False
        global socket_sender_predict_running
        socket_sender_predict_running = False


"""main func """
#main func.
if __name__ == '__main__':
    svc_port = int(os.environ.get('SERVICE_PORT', SERVICE_PORT))
    LOG.info('serice started listening port: %d', svc_port)
    #init data.
    init()
    socketio.run(app, port=svc_port, host='0.0.0.0',debug=IS_DEBUG)


