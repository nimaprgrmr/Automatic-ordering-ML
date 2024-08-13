import pandas as pd 
import numpy as np 
import math
from datetime import datetime
import warnings 
warnings.filterwarnings('ignore')
from flask import Flask, jsonify
import statistics


# initialize app name 
app = Flask(__name__)


def read_data(path='data.csv'): 
    df = pd.read_csv(path, header=None)
    columns = ['IdHdr', 'IdClient', 'ClientName', 'Amount', 'DscItem', 'IdItem', 'Date', 'ItemType', 'IdItemType','min']
    df.columns = columns
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S.%f')
    df['Date'] = df["Date"].dt.date
    # sort values base on date column 
    df = df.sort_values(by='Date')
    df = df.drop_duplicates()
    return df


def make_period_time(df: pd.DataFrame, days:int=61):
    # now = datetime.today().date()
    now = pd.to_datetime('2023-11-24')
    now = now.date()
    df['Recently'] = now - df['Date']
    
    def make_true(column):
        if column.days > days:
            return False
        else:
            return True
    
    df['Assess'] = df['Recently'].apply(make_true)
    df1 = df[df['Assess'] == True]
    return df1 


def calculate_max_orders(period_df: pd.DataFrame, std_criterion:float=2):
    list_names = period_df['ClientName'].unique()
    list_items = period_df['DscItem'].unique()
    
    period_df['Mean'] = 0.
    period_df['Std'] = 0.
    for name in list_names[0:]:
        for item in list_items[0:]:
            if item in (period_df[period_df['ClientName'] == name]['DscItem'].unique()):
                items = period_df[(period_df['ClientName']==name) & (period_df['DscItem']==item)]['Amount']
                mean = items.mean()
                try:
                    # Calculate sum of squared differences from the mean
                    squared_diffs = sum((x - mean) ** 2 for x in items)
                    # Calculate population standard deviation
                    std = (squared_diffs / len(items)) ** 0.5
                    # std = statistics.stdev(items)
                except:
                    std = 0
                period_df.loc[(period_df['ClientName'] == name) & (period_df['DscItem'] == item), 'Mean'] = mean
                period_df.loc[(period_df['ClientName'] == name) & (period_df['DscItem'] == item), 'Std'] = std
    
    period_df['Std'] = period_df['Std'].fillna(0)
    period_df['StdCriterion'] = std_criterion
    period_df['Max'] = (period_df['Std'] * period_df['StdCriterion']) + period_df['Mean']
    period_df['Max'] = period_df['Max'].apply(lambda x: math.ceil(x))
    
    return period_df


def find_max(id_client:int=0, id_item:int=0):
    df = read_data()
    period_df = make_period_time(df)
    last_df = calculate_max_orders(period_df, std_criterion=2.0)
    # max_value = last_df[(last_df['IdClient']==id_client) & (last_df['IdItem']==id_item)]['Max']
    # max_value = max_value.iloc[-1]
    max_df = last_df[['IdClient', 'IdItem', 'IdItemType', 'min', 'Std', 'StdCriterion', 'Max']]
    max_df = max_df.drop_duplicates()
    # max_df.sort_values(by=max_df['IdClient'])
    return max_df


# print(find_max(id_client=21761222, id_item=1061001))
# max_df = find_max()
# print(max_df[(max_df['IdClient']==21761222) & (max_df['IdItem'] == 1061001)])

@app.route('/get_max_data', methods=['GET'])
def get_max_data():
    max_df = find_max()
    json_data = max_df.to_json(orient='records')  # Convert DataFrame to JSON
    return jsonify(data=json_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
