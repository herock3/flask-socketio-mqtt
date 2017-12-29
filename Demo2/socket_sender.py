from common_func import *

class SocketSender(threading.Thread):
    '''send socket message.'''
    def __init__(self, socketio, is_predict, queue):
        threading.Thread.__init__(self)
        self.socketio = socketio
        self.is_predict = is_predict
        self.queue = queue
    #thread.
    def run(self):
        LOG.info('****socket sender thread start, is predict:{}'.format(self.is_predict))
        global mqttc_dict
        try:
            while True:
                if not len(mqttc_dict):
                    break
                LOG.debug('===socket sender thread running, is predict:{} ....'.format(self.is_predict))
                #get msg.
                msg = self.queue.get()
                #send msg.
                if self.is_predict:
                    self.socketio.emit('message_response_predict', json.dumps(dict(status=200, result=msg)), namespace='/socket') 
                else:
                    self.socketio.emit('message_response_sensor', json.dumps(dict(status=200, result=msg)), namespace='/socket')

                LOG.debug('...sending response message:{}'.format(json.dumps(dict(status=200, result=msg))))
        except Exception as ex:
            LOG.error('error happens in socket sender: {}'.format(str(ex)))   

