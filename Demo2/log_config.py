import logging
from logging.handlers import RotatingFileHandler
import os

LOG_HOME = os.getcwd() + '/' + 'log'
if not os.path.exists(LOG_HOME):
    os.makedirs(LOG_HOME)

LOG = logging.getLogger('flask-service')
fileHandler =  RotatingFileHandler(LOG_HOME + '/flask-service.log', maxBytes=20*1024*1024,backupCount=5)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fileHandler.setFormatter(formatter)
LOG.addHandler(fileHandler) 
LOG.setLevel(logging.DEBUG)
LOG.propagate = False

