import pandas as pd 
import numpy as np 
from sklearn.neighbors import KNeighborsClassifier
import statistics as st 
from calculate_max import read_data, make_period_time
from keras.preprocessing.sequence import pad_sequences
import warnings
warnings.filterwarnings('ignore')
import pickle


def make_data_ready():
    df = read_data()
    df1 = make_period_time(df, days=61)
    df1['IdClient'] = df1['IdClient'].astype(str)
    df1['IdItem'] = df1['IdItem'].astype(str)
    df1['Date'] = df1['Date'].astype(str)
    len_client = len(df1['IdClient'].iloc[0]) 
    len_item = len(df1['IdItem'].iloc[0])
    update_df = df1[['IdHdr', 'IdClient', 'IdItem', 'ItemType', 'Date']].groupby('IdHdr', as_index=True).sum()
    update_df['IdClient'] = update_df['IdClient'].apply(lambda x:  x[:len_client])
    
    def make_item(string):
        formatted_string = '-'.join([string[i:i+len_item] for i in range(0, len(string), len_item)])
        return formatted_string

    update_df['IdItem'] = update_df['IdItem'].apply(make_item)
    
    def make_type(string):
        if 'روزانه' in string:
            return 201
        elif 'یخچالی' in string:
            return 1
        else:
            return 101
    
    update_df['ItemType'] = update_df['ItemType'].apply(make_type)
    
    def make_date(column):
        date = column[0:10]
        return date 

    update_df['Date'] = update_df['Date'].apply(make_date)
    
    def make_item(column):
        column = column.split('-')
        for i, item in enumerate(column):
            item = int(item)
            column[i] = item
        return column

    update_df['IdItem'] = update_df['IdItem'].apply(make_item)
    update_df['IdClient'] = update_df['IdClient'].astype(int)
    update_df['ItemType'] = update_df['ItemType'].astype(int)
    
    return update_df, df1 


def train_model():
    update_df, df1 = make_data_ready()
    train = update_df[update_df['Date'] < '2023-11-13']
    test = update_df[update_df['Date'] >= '2023-11-13']
    X_train, y_train = train[['IdClient', 'ItemType']].values, train['IdItem']
    X_test, y_test = test[['IdClient', 'ItemType']].values, test['IdItem']
    # Pad the target data with zeros to make each row of equal length
    max_length = max([len(row) for row in update_df['IdItem']])
    y_train = pad_sequences(train['IdItem'], maxlen=max_length, padding='post')
    y_test = pad_sequences(test['IdItem'], maxlen=max_length, padding='post')    

    from sklearn.neighbors import KNeighborsClassifier 
    model_knn = KNeighborsClassifier(n_neighbors=1, algorithm='brute')
    model_knn.fit(X_train, y_train)
    # preds_knn = model_knn.predict(X_test)
    
    return model_knn 


def save_model(model, path: str):
    # save
    with open(path,'wb') as f:
        pickle.dump(model, f)

if __name__ == "__main__":    
    model = train_model()
    save_model(model, path='model.pkl')
    