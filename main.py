"""
Main API structure to return the Space weather, Beacon, TLE and conjunction data
"""
import pandas as pd
from fastapi import FastAPI, HTTPException
from GetData import twotle,conjunction,satelliteTLE,telemetry_data
import json
from datetime import datetime
from TLE import satdata
app = FastAPI()

# Define or import your functions here, such as calculate_checksum, fractionalday, format_tle, get_satellite_tle
@app.get("/tle/{norad_cat_id}")
async def get_tle(norad_cat_id: int):
    tle_dict=satelliteTLE(norad_cat_id)
    if tle is None:
        raise HTTPException(status_code=404, detail="TLE not found for the given NORAD Catalog ID")
    return {"tle": tle_dict}

@app.get("/tle")
async def tle():
    df=twotle()
    json_str = df.to_json(orient='records' ,date_format='iso')
    parsed = json.loads(json_str)
    return {"Date": datetime.today(), '\n TLE': parsed}

@app.get("/conjunction/{norad_cat_id}")
async def cdm(norad_cat_id: int):
    df=conjunction()
    result = df[(df['NORAD_CAT_ID_1'] == norad_cat_id) | (df['NORAD_CAT_ID_2'] == norad_cat_id)]
    json_str = result.to_json(orient='index', date_format='iso')
    parsed = json.loads(json_str)
    if result is None:
        raise HTTPException(status_code=404, detail="No CDM messages found for the given NORAD Catalog ID")
    return {"Norad Cat Id :": int(norad_cat_id), f"Conjunction Messages for {norad_cat_id} ": parsed}

@app.get("/telemetry/{norad_cat_id}")
async def get_tle(norad_cat_id: int):
    data=telemetry_data(norad_cat_id)
    json_str = data.to_json(orient='split', date_format='iso')
    parsed = json.loads(json_str)
    if data is None:
        raise HTTPException(status_code=404, detail="Telemetry not found for the given NORAD Catalog ID")
    return {f"Telemetry data for {norad_cat_id}": parsed}

@app.get("/satellitepass/{norad_cat_id}")
async def satpass(norad_cat_id):
        pass_data=satdata(int(norad_cat_id),10)
        data=pd.DataFrame(pass_data)
        print(data.head())
        json_str = data.to_json(orient='index', date_format='iso')
        parsed = json.loads(json_str)
        return {f"Satellites pass data for {norad_cat_id}": parsed}

