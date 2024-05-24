"""
Code to collect space weather data from multiple sources and processing into suitable format
"""
import pandas as pd
from io import StringIO
import requests
from joblib import Parallel, delayed
from datetime import datetime, timedelta
import datetime


def esa_data():
    """
    Retrieve and process the solar weather data from the ESA Solmag

    :return: Pandas series object
    """
    # URL of the REST API endpoint
    url = 'https://static.sdo.esoc.esa.int/SOLMAG/fap_day.dat'

    # Make a GET request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Assuming the .dat file is tab-delimited. Modify delimiter as needed.
        df = pd.read_csv(StringIO(response.text), delimiter=' ')
    else:
        print("Failed to retrieve the .dat file. Status code:", response.status_code)

    #Data processing
    start_col_index = 6
    end_col_index = 22
    columns_to_drop = df.iloc[:, start_col_index:end_col_index + 1].columns
    # Drop the selected columns
    df.drop(columns=columns_to_drop, axis=1, inplace=True)
    df = df.rename(columns={'Unnamed: 5': '3 hr Kp Indices'})
    #Delete the row
    df = df.drop(0).reset_index(drop=True)
    today = datetime.date.today().strftime("%d/%m/%Y")
    index = df[df['#d/mm/yyyy'] == today].index
    df = df.astype({'Ap': int, 'F10': int})
    return df.iloc[index]


def esaData_JR(df, input_date):
    """
    Formatting the celestrak data to be suitable for Jacchia Bowman models

    :param df:
    :param input_date:
    :return: String
    """
    # Parse the input date string
    # Convert date column to datetime
    df['#d/mm/yyyy'] = pd.to_datetime(df['#d/mm/yyyy'], dayfirst=True)
    df['DATE_str'] = df['#d/mm/yyyy'].dt.strftime('%Y-%m-%d')
    input_date_str = input_date.strftime('%Y-%m-%d')

    # Check for the presence of input_date_str in the DataFrame
    if input_date_str in df['DATE_str'].values:
        idx = df.index[df['DATE_str'] == input_date_str].tolist()
    else:
        return "Date not found in dataset."

    idx = idx[0]

    # Select the data for 1 previous day and the next 5 days
    selected_data = df.iloc[max(idx - 1, 0):min(idx + 6, len(df))]

    # Format the data into a string
    formatted_data = ""
    for _, row in selected_data.iterrows():
        date_str = row['#d/mm/yyyy'].strftime('%b %d %Y').upper()
        f10, f3m, ssn, ap = row['F10'], row['F3M'], row['SSN'], row['Ap']
        kp_indices = '   '.join([f"{float(k):.3f}" if k.strip() else 'NaN' for k in row['Kp_Indices']])

        formatted_data += f"{date_str}    {f10} {kp_indices}\n"

    return formatted_data

def gfz_data():
    """
    Retriving space weather data
    Data Source: Geomagnetic Observatory Niemegk, GFZ German Research Centre for Geosciences
    :return: Pandas series object
    """
    url = 'https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_Ap_SN_F107_nowcast.txt'

    # Parameters (if applicable)
    params = {
        'start_year': 1932,  # Example: parameter to specify the start year
        # Add any other relevant parameters here
    }

    # Make a GET request to the API with streaming enabled
    with requests.get(url, params=params, stream=True) as response:
        # Check if the request was successful
        if response.status_code == 200:
            data=response.text
        else:
            print("Failed to retrieve the file. Status code:", response.status_code)

    columns = ['Year', 'Month', 'Day', 'days', 'days_m', 'Bsr', 'dB', 'Kp1', 'Kp2', 'Kp3', 'Kp4', 'Kp5', 'Kp6', 'Kp7', 'Kp8',
               'ap1', 'ap2', 'ap3', 'ap4', 'ap5', 'ap6', 'ap7', 'ap8', 'Ap', 'SN', 'F10.7obs', 'F10.7adj', 'D']

    # Use StringIO to convert the string data into a file-like object
    data_io = StringIO(data)

    # Create a DataFrame, considering the data is space-separated
    df = pd.read_csv(data_io, sep="\s+", names=columns, comment='#')
    df['DateString'] = pd.to_datetime(df[['Day', 'Month', 'Year']])
    df['Date'] = df['DateString'].dt.strftime('%d/%m/%Y')
    df = df.astype({'Ap': int, 'F10.7obs': int})
    return df.iloc[-2]
