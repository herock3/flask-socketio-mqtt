from socket_sender import *

#import model.
import models.predictive_maintenance.Rul as Rul
import pandas as pd

global predict_model

predict_model = Rul.Rul()
predict_model.init('models/predictive_maintenance/pm.h5')

#sequence_length = predict_model.get_sequence_length()
#read test data
#data = pd.read_csv('models/predictive_maintenance/PM_test.txt', sep=" ", header=None)
#data.drop(data.columns[[26, 27]], axis=1, inplace=True)
#data.columns = ['id', 'cycle', 'setting1', 'setting2', 'setting3', 's1', 's2', 's3',
#                   's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12', 's13', 's14',
#                   's15', 's16', 's17', 's18', 's19', 's20', 's21']

#print('sequence_length:', sequence_length)
#test_df = data[1 : 1+sequence_length]
#    #print(test_df.head())
#result = predict_model.predict(test_df)
#print(result)

