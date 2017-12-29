import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn import preprocessing
import keras.backend as K

def rmse(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true), axis = -1))


# function to reshape features into (samples, time steps, features)
def gen_sequence(id_df, seq_length, seq_cols):
    """ Only sequences that meet the window-length are considered, no padding is used. This means for testing
        we need to drop those which are below the window-length. An alternative would be to pad sequences so that
        we can use shorter ones """
    data_array = id_df[seq_cols].values
    num_elements = data_array.shape[0]
    for start, stop in zip(range(0, num_elements-seq_length), range(seq_length, num_elements)):
        yield data_array[start:stop, :]

class Rul(object):
    def __init__(self):
        pass

    def init(self, modelPath):
        self.model = load_model(modelPath, custom_objects = {'rmse' : rmse})
        self.sequence_length = 6
        train_df = pd.read_csv('models/predictive_maintenance/PM_train.txt', sep=" ", header=None)
        train_df.drop(train_df.columns[[26, 27]], axis=1, inplace=True)
        train_df.columns = ['id', 'cycle', 'setting1', 'setting2', 'setting3', 's1', 's2', 's3',
                    's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12', 's13', 's14',
                    's15', 's16', 's17', 's18', 's19', 's20', 's21']
        self.cols_normalize = train_df.columns.difference(['id','cycle'])
        self.min_max_scaler = preprocessing.MinMaxScaler()
        norm_train_df = pd.DataFrame(self.min_max_scaler.fit_transform(train_df[self.cols_normalize]),
                             columns=self.cols_normalize,
                             index=train_df.index)

    def get_sequence_length(self):
        return self.sequence_length
  
    
    def predict(self, test_df):
        try:
            #cols_normalize = test_df.columns.difference(['id','cycle'])
            #min_max_scaler = preprocessing.MinMaxScaler()
            norm_test_df = pd.DataFrame(self.min_max_scaler.transform(test_df[self.cols_normalize]),
                                       columns=self.cols_normalize,
                                       index=test_df.index)
            test_join_df = test_df[test_df.columns.difference(self.cols_normalize)].join(norm_test_df)
            test_df = test_join_df.reindex(columns = test_df.columns)
            test_df = test_df.reset_index(drop=True)
            #print(test_df)
    
            sequence_cols = ['setting1', 'setting2', 'setting3', 's2', 's3', 's4', 's6', 's7', 's8', 's9', 's11', 's12', 's13', 's14', 's15', 's17', 's20', 's21']
    #sequence_cols = ['s2', 's3', 's4', 's6', 's7', 's8', 's9', 's11', 's12', 's13', 's14', 's15', 's17', 's20', 's21']
            # generator for the sequences
            seq_gen = (list(gen_sequence(test_df[test_df['id']==id], self.sequence_length, sequence_cols))
                    for id in test_df['id'].unique())
                    #print(list(seq_gen).shape())
            # generate sequences and convert to numpy array
            seq_array = np.concatenate(list(seq_gen)).astype(np.float32)
            #print(seq_array.shape)

            seq_array_test = test_df[sequence_cols].values
            #for id in test_tf['id'].unique()
            #print(seq_array_test.shape[0], seq_array_test.shape[1])
            #print(test_df.head())
            seq_array_test = seq_array_test.reshape(1, seq_array_test.shape[0], seq_array_test.shape[1])
            seq_array_test = np.asarray(seq_array_test).astype(np.float32)
            preds = self.model.predict(seq_array_test)
            return preds[0]
        except Exception as e:
            print(str(e))
            return 0

