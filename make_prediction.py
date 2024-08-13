import numpy as np 
import pandas as pd 
import pickle
from sklearn.neighbors import KNeighborsClassifier 
from calculate_max import read_data, make_period_time
import statistics as st 
from flask import Flask, jsonify, request


app = Flask(__name__)

def upload_model(path:str='model.pkl'):
    # load
    with open(path, 'rb') as f:
        model_knn = pickle.load(f)
        return model_knn
    
def make_predictions(id_client:int, id_itemtype:int):
    model_knn = upload_model()
    sample = [np.array([id_client, id_itemtype])]
    pred = model_knn.predict(sample)
    pred = set(pred[0])
    pred.remove(0)
    
    
    df = read_data()
    df1 = make_period_time(df, days=61)
    
    # print(df1.head())
    final_result = {}
    for p in pred:
        amount_p = (df1[df1['IdItem'] == p]['Amount'])
        mode_p = st.mode(amount_p)
        final_result[p] = mode_p

    return final_result 

# prediction = make_predictions(id_client=21742022, id_itemtype=201)
# print(prediction)


def convert_float64_to_python_types(data):
    for key, value in data.items():
        data[key] = value.item() if isinstance(value, np.float64) else value
    return data

@app.route('/get_predictions', methods=['POST'])
def get_predictions():
    data = request.get_json()
    id_client = data['id_client']
    id_itemtype = data['id_itemtype']
    
    prediction = make_predictions(id_client=id_client, id_itemtype=id_itemtype)
    prediction = convert_float64_to_python_types(prediction)
    
    # Manually convert the dictionary to a standard Python dictionary
    result_dict = {}
    for key, value in prediction.items():
        result_dict[str(key)] = value
    
    return jsonify(result_dict)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
    