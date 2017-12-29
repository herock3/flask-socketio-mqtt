import Rul
import pandas as pd

rul = Rul.Rul()
model = rul.init('pm.h5')
sequence_length = rul.get_sequence_length()
#read test data
data = pd.read_csv('PM_test.txt', sep=" ", header=None)
data.drop(data.columns[[26, 27]], axis=1, inplace=True)
data.columns = ['id', 'cycle', 'setting1', 'setting2', 'setting3', 's1', 's2', 's3',
                   's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12', 's13', 's14',
                   's15', 's16', 's17', 's18', 's19', 's20', 's21']

print('sequence_length:', sequence_length)
test_df = data[1 : 1+sequence_length]
#    #print(test_df.head())
result = rul.predict(test_df)
print(result)

#for i in range(5):
#    test_df = data[i : i+sequence_length]
#    #print(test_df.head())
#    result = rul.predict(test_df)
#    print(result)
    
