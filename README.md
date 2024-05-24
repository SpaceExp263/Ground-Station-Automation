# SaRC Ground Station Automation

## Overview
This project encompasses three main components, developed as part of an internship at the Satellite Research Centre at Nanyang Technological University. The tasks focused on ground station automation for efficient satellite operations, aiming to streamline and enhance the efficiency of satellite data collection, processing, and analysis. By automating these processes, the project reduces the need for manual intervention, minimizes errors, and ensures timely and accurate data availability. This approach supports more effective satellite monitoring, control, and prediction capabilities, ultimately contributing to the overall resilience and reliability of satellite missions.

This project encompasses three main components:

**SatelliteData API**: Involves GetData.py, TLE.py, and main.py for fetching and processing satellite data.

**Space Weather Database**: Uses SpaceWeatherObserved.py and SpaceWeatherPrediction.py to collect and store observed and predicted space weather data.

**Ensemble Model for F10.7 Prediction**: Includes timeseriesanalysis.py for predicting F10.7 using LSTM, Facebook Prophet, and Gradient Booster models.


## Dependencies
### SatelliteData API

1. GetData.py: Fetches and processes data from Celestrak, SatNOGS, and Space-Track. Ensure to replace your Space-Track credentials  in GetData.py.

2. TLE.py: Retrieves and processes Two-Line Element (TLE) data.

### Space Weather Database

1. SpaceWeatherObserved.py: Collects observed space weather data.
2. SpaceWeatherPrediction.py: Retrieves predicted space weather data.

### Time Series Analysis
timeseriesanalysis.py: Predicts F10.7 using LSTM, Facebook Prophet, and Gradient Booster models.

Datasets:
gfz.xlsx: Used for training the LSTM and Facebook Prophet models.
solar_data_segments.xlsx (sheet: F10.7): Used for training the Gradient Booster model.

## Instructions
1. SatelliteData API
    1. Replace Space-Track Credentials:

        - Open GetData.py.
        - Replace placeholder credentials with your Space-Track credentials.
          

    2. Run the API:

        - Open the terminal.
        - Navigate to the directory containing the code files.
        - Execute the following command:
        `uvicorn main:app
`
2. Space Weather Database
    1. Retrieve and Store Data:

        - Observed Data: Run SpaceWeatherObserved.py to collect observed space weather data.
        - Predicted Data: Run SpaceWeatherPrediction.py to retrieve predicted space weather data.
        - Ensure the data is stored in an Excel file named spaceweather.xlsx in the datasets folder.


    2. Daily Updates:

        - Schedule the retrieval scripts to run daily to ensure the database is up-to-date.

3. Ensemble Model for F10.7 Prediction
    1. Upload Files to Google Colab:

        - Upload timeseriesanalysis.py to your Google Colab environment.

    2. Run the Script:

        - Open timeseriesanalysis.py in Google Colab.
        - Upload gfz.xlsx and solar_data_segments.xlsx when prompted by Colab for LSTM and Gradient Booster respectively. 
        - Execute the script to train the LSTM, Facebook Prophet, and Gradient Booster models.
        - **Note:** Training these models in Google Colab is recommended due to the high computational power required.



## Project Structure

- GetData.py: Fetches and processes satellite data.
- TLE.py: Retrieves and processes TLE data.
- main.py: Main API script to run the SatelliteData API.
- SpaceWeatherObserved.py: Collects observed space weather data.
- SpaceWeatherPrediction.py: Retrieves predicted space weather data.
- timeseriesanalysis.py: Time series analysis and F10.7 prediction using ensemble models.
- datasets/: Folder containing dataset files (gfz.xlsx, solar_data_segments.xlsx, spaceweather.xlsx).

## Additional Notes

- Ensure to upload the entire folder with all the code files, as these .py files are interdependent on each other to run effectively.
- Regularly update your datasets and credentials to maintain the accuracy and functionality of the API and models.
