# step 1 - import modules
import requests
import json

from airflow import DAG
from datetime import datetime
from datetime import date
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator

import tweepy
import pandas as pd
import numpy as np
from textblob import TextBlob
  
# step 2 - define default args
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False
    # 'start_date': datetime(2020, 12, 25)
    }


# step 3 - instantiate DAG
dag = DAG(
    'M3-DAG',
    start_date= datetime(2021, 1, 9),
    end_date= datetime(2021, 1, 13),
    default_args=default_args,
    description='Milestone 3 of Data Engineering',
    schedule_interval='@daily',
    catchup = True
)

def extract(**kwargs):
    credentials = {}
    credentials['CONSUMER_KEY'] = "VGQ7a4RznOFgvEs4BGj81sETP"
    credentials['CONSUMER_SECRET'] = "jC6kXo83aMQnatiBwcxriqakmEfEe0CmY3CiU9222oD4oier2j"
    credentials['ACCESS_TOKEN'] = "850371908566740993-onXJPP2dgRqyMwk4wEaAarrOuLAs1EZ"
    credentials['ACCESS_SECRET'] = "9P9r62OOht2ZnZpsWpBJylYnDniFX6WNYuBOCf8WhKjzL"

    # Save the credentials object to file
    with open("/home/hashem/twitter_credentials.json", "w") as file:
        json.dump(credentials, file)
    with open("/home/hashem/twitter_credentials.json", "r") as file:
        creds = json.load(file)
    auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    auth.set_access_token(creds['ACCESS_TOKEN'],creds['ACCESS_SECRET'])
    print("hello")
    api = tweepy.API(auth)
    print("hello")
    places = api.geo_search(query="Finland", granularity="country")
    place_id = places[0].id
    # place_id='e7c97cdfef3a741a'
    print("here")
    tweets_Finland = api.search(q="place:%s"  % place_id, result_type='recent',count=100,lang ='en')
    print("hello")
    dict_ = {'user': [], 'date': [], 'text': [], 'country': []}
    for tweet in tweets_Finland:
        dict_['user'].append(tweet.user.name)
        dict_['date'].append(tweet.created_at)
        dict_['text'].append(tweet.text)
        dict_['country'].append(tweet.place.country)

    # Structure data in a pandas DataFrame for easier manipulation
    df_Finland = pd.DataFrame(dict_)
    df_Finland=df_Finland[0:20]
    try:
        df_data = pd.read_csv('/home/hashem/df_Finland.csv')
        df_Finland = pd.concat([df_data, df_Finland])
        df_Finland.reset_index()
        df_Finland.to_csv('/home/hashem/df_Finland.csv', index = False)
        df_Finland = pd.read_csv('/home/hashem/df_Finland.csv')
    
    except FileNotFoundError: 
        df_Finland.to_csv('/home/hashem/df_Finland.csv' , index = False)

    places = api.geo_search(query="Togo", granularity="country")
    place_id = places[0].id
    # place_id='e7c97cdfef3a741a'
    tweets_Togo = api.search(q="place:%s"  % place_id, result_type='recent',land='eng',count=100)
    dict_ = {'user': [], 'date': [], 'text': [], 'country': []}
    for tweet in tweets_Togo:
        dict_['user'].append(tweet.user.name)
        dict_['date'].append(tweet.created_at)
        dict_['text'].append(tweet.text)
        dict_['country'].append(tweet.place.country)

    # Structure data in a pandas DataFrame for easier manipulation
    df_Togo = pd.DataFrame(dict_)
    df_Togo=df_Togo[0:20]
    try:
        df_data = pd.read_csv('/home/hashem/df_Togo.csv')
        df_Togo = pd.concat([df_data, df_Togo])
        df_Togo.reset_index()
        df_Togo.to_csv('/home/hashem/df_Togo.csv', index = False)
        df_Togo = pd.read_csv('/home/hashem/df_Togo.csv')
    
    except FileNotFoundError: 
        df_Togo.to_csv('/home/hashem/df_Togo.csv' , index = False)

    return df_Finland,df_Togo

def transform(**context):
    df_Finland,df_Togo= context['task_instance'].xcom_pull(task_ids='extract')
    df_Finland['index'] = df_Finland.index
    indices = df_Finland['index'].unique()
    for i in indices:
        text = df_Finland[df_Finland['index']==i]['text']
        result = TextBlob(text[i]).polarity
        result_scaled = (result+1)*5
        df_Finland.loc[df_Finland['index']==i, 'sentiment analysis']= result_scaled
    score_average_Finland= df_Finland.groupby(['country'])['sentiment analysis'].mean()

    df_Togo['index'] = df_Finland.index
    indices = df_Togo['index'].unique()
    for i in indices:
        text = df_Togo[df_Togo['index']==i]['text']
        result = TextBlob(text[i]).polarity
        result_scaled = (result+1)*5
        df_Togo.loc[df_Togo['index']==i, 'sentiment analysis']= result_scaled
    score_average_Togo= df_Togo.groupby(['country'])['sentiment analysis'].mean()
    return score_average_Finland,score_average_Togo

def load(**context):
    score_average_Finland,score_average_Togo=context['task_instance'].xcom_pull(task_ids='transform')
    ct = datetime.now() 
    score_average_Finland=pd.Series.to_frame(score_average_Finland)
    score_average_Finland['time'] = ct
    score_average_Togo=pd.Series.to_frame(score_average_Togo)
    score_average_Togo['time'] = ct
    day = ct.strftime("%d")
    month = ct.strftime("%m")
    day_month = day+"-"+month
    file_name = "Finland %s" %day_month
    score_average_Finland.to_csv("/home/hashem/"+file_name)
    file_name = "Togo %s" %day_month
    score_average_Togo.to_csv("/home/hashem/"+file_name)

    





t1 = PythonOperator(
    task_id='extract',
    provide_context=True,
    python_callable=extract,
    dag=dag,
)

t2 = PythonOperator(
    task_id='transform',
    provide_context=True,
    python_callable=transform,
    dag=dag,
)
t3 = PythonOperator(
    task_id='load',
    provide_context=True,
    python_callable=load,
    dag=dag,
)

# step 5 - define dependencies
t1 >> t2 >> t3
