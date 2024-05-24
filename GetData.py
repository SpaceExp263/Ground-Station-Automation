
"""
TLE and CDM data from various sources is taken and processed
"""
from joblib import Parallel, delayed
import pandas as pd
from io import StringIO
from pandas import json_normalize
import requests
from spacetrack import SpaceTrackClient
import pandas as pd
from datetime import datetime,timedelta
from TLE import satdata
import math
# spacetrack password and identity

identity='palak002@e.ntu.edu.sg'
password='PalakPorwalrocks15'

def twotle():
    st = SpaceTrackClient(identity=identity, password=password)
    #tle=st.tle(norad_cat_id=id, orderby='epoch desc', limit=1, format='tle')
    tle=st.tle_latest(ordinal=1, epoch='>now-30',limit=40)
    df = pd.DataFrame(tle)
    df = df.drop(df[df['OBJECT_TYPE'] == 'UNKNOWN'].index)
    df = df[df['OBJECT_TYPE'] == 'PAYLOAD']
    columns_to_keep = ['NORAD_CAT_ID', 'EPOCH', 'OBJECT_NAME', 'TLE_LINE1', 'TLE_LINE2']
    df = df.drop(columns=set(df.columns) - set(columns_to_keep), axis=1)
    return df

def chunks(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def conjunction_ST():
    """
    Conjunction data from Space Track is processed
    :return: Dataframe
    """
    st = SpaceTrackClient(identity=identity, password=password)
    df=pd.DataFrame(st.cdm_public())
    columns_to_delete = ["CREATED", "SAT1_RCS","SAT_1_EXCL_VOL","SAT2_RCS","SAT_2_EXCL_VOL"]
    df = df.drop(columns=columns_to_delete, axis=1)
    df['TCA'] = pd.to_datetime(df['TCA'])
    # Sort the DataFrame by the 'tca' column in descending order
    df_sorted = df.sort_values(by='TCA', ascending=False)
    today=datetime.today()
    final_df = df_sorted[df_sorted['TCA'] >= today]
    final_df.rename(columns={"TCA": "Time of Closest Approach", "PC": "Probability of Collision", "MIN_RNG": "Minimum Range"},inplace=True)
    return final_df

def conjunction():
    """
    Conjunction data from Celestrak is processed
    :return: Dataframe
    """
    url = 'https://celestrak.org/SOCRATES/sort-minRange.csv'
    # # Fetch the content of the text file
    df=pd.read_csv(url)
    df['TCA'] = pd.to_datetime(df['TCA'])
    today=datetime.today()
    final_df = df[df['TCA'] >= today].copy()
    final_df.sort_values(by='TCA', ascending=True, inplace=True)
    final_df.rename(columns={"TCA": "Time of Closest Approach", "MAX_PROB": "Probability of Collision", "TCA_RANGE": "Minimum Range","TCA_RELATIVE_SPEED":"Relative Speed"},inplace=True)
    st = SpaceTrackClient(identity=identity, password=password)
    return final_df

def satelliteTLE(satid):
    st = SpaceTrackClient(identity=identity, password=password)
    tle = st.tle(norad_cat_id=satid, orderby='epoch desc', limit=1, format='tle')
    lines = tle.split("\n")
    tle_dict = {}
    for i, line in enumerate(lines[:2], start=1):
        tle_dict[f"TLE{i}"] = line
    return lines

def telemetry_data(norad_cat_id):
    url="https://network.satnogs.org/api/observations/"
    response=requests.get(url,params={"satellite__norad_cat_id":norad_cat_id}).json()
    df=pd.DataFrame(response)
    return df


