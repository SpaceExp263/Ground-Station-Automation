"""
Program to get the predicted space weather data from multiple sources and updating the Excel
"""
import pandas as pd
import requests
from SpaceWeatherObserved import esa_data,gfz_data
from datetime import datetime, timedelta
from openpyxl import load_workbook

dates = []
ap = []
f10 = []

def processAp(data):
    for i in range(0,len(data)):
        if i%2 !=0:
            ap.append(int(data[i]))
        else:
            original_date = datetime.strptime(data[i], '%d%b%y')
            # Format the datetime object with the new format
            date = original_date.strftime("%d/%m/%Y")
            dates.append(date)

def processf10(data):
    for i in range(0,len(data)):
        if i%2 != 0:
            f10.append(int(data[i]))

def weatherpred():
    """
    Method to retrieve and process Space Weather Data from NOAA. The method stores the next 45 day prediction for Ap and the F10.7 Values
    :return: None
    """
    url = 'https://services.swpc.noaa.gov/text/45-day-ap-forecast.txt'
    # Fetch the content of the text file
    response = requests.get(url)
    data = response.text
    # Split the text into lines
    lines = data.split('\n')
    # Initialize variables to store data
    date_values = []
    check=0
    #if check is 0, then Ap values are being processed and if check is 1, then kp values are being processed
    # Iterate through lines and extract data
    for line in lines:
        if line.startswith(':Issued:') or line.startswith('#') or line.startswith(':') or line.strip() == '' or line.startswith("FORECASTER:") or line.startswith("99999") or line.startswith('NNNN') or line.startswith("45-DAY AP FORECAST"):
            # Skip comments and empty lines
            continue
        elif line.startswith("45-DAY F10.7 CM FLUX FORECAST"):
            check=1
        else:
            # Extract date-value pairs
            date = line.split(' ')
            if check==0:
                processAp(date)
            else:
                processf10(date)


def esa_weatherpred():
    """
    Method to retrieve and process SOLMAG data. The method stores the 27 day predictions for the Ap and F10 values
    :return: List
    """
    length=len(dates)
    eap=[0] * length
    ef10=[0] * length
    url = 'https://static.sdo.esoc.esa.int/SOLMAG/short_term.dat'
    # Fetch the content of the text file
    response = requests.get(url)
    data = response.text
    lines = data.split('\n')
    index_to_delete_up_to = lines.index('#--------- --- --- --- --- ---------------   27d forecast -> nominal')
    # Use list slicing to delete values up to the specified index
    lines = lines[index_to_delete_up_to:]
    indices1 = lines.index('#--------- --- --- --- --- ---------------   27d forecast -> nom+95%')
    indices2 = lines.index('#--------- --- --- --- --- ---------------   27d forecast -> nom-95%')
    # Assuming there is always at least one line matching each substring
    nominal = lines[1:indices1-2]
    for line in nominal:
        line_list = line.split(" ")
        date=line_list[0]
        if date in dates:
            index = dates.index(date)
            ef10[index]=int(line_list[1])
            eap[index]= int(line_list[4])
        else:
            continue
    return ef10,eap

def celestrakpred():
    """
    Method to collect observed and predicted data from celestrak and process it to store in the excel sheet
    :return: list
    """
    ctrak = []
    url="https://celestrak.org/SpaceData/SW-Last5Years.txt"
    response = requests.get(url)
    data = response.text
    lines = data.split('\n')
    index_to_delete_up_to = lines.index('BEGIN OBSERVED\r')
    index_to_delete_from=lines.index('END DAILY_PREDICTED\r')
    # Use list slicing to delete values up to the specified index
    lines = lines[index_to_delete_up_to+1:index_to_delete_from]
    observed=lines[:lines.index('END OBSERVED\r')]
    predicted=lines[lines.index('BEGIN DAILY_PREDICTED\r')+1:]
    today_observed=processlist(observed[-1])
    for line in predicted:
        ctrak.append(processlist(line))
    return today_observed,ctrak

def processlist(temp):
    curr=[]
    data=[item for item in temp.split(" ") if item]
    # Extract year, month, and day
    year = int(data[0])
    month = int(data[1])
    day = int(data[2])
    # Create a datetime object and format it into a date string
    date_string = datetime(year, month, day).strftime('%d/%m/%Y')
    curr.append(date_string)
    curr.append(data[22])
    curr.append(data[29])
    return curr

def updateExcel():
    """
    Method to create a new sheet to store the daily predicted data and to store the daily observed values in the existing excel sheets
    :return: None
    """
    path= r"C:\Users\Palak002\Downloads\spaceweather.xlsx"
    xls = pd.ExcelFile(path)
    num_sheets = len(xls.sheet_names)
    print(num_sheets)
    f'Sheet{num_sheets + 1}'
    weatherpred()
    ef10, eap=esa_weatherpred()
    today_ctrak, ctrak=celestrakpred()
    ceap=[]
    cef10=[]

    for i in ctrak:
        ceap.append(float(i[1]))
        cef10.append(float(i[2]))

    empty_list=[0]*len(dates)
    dict={"Date":dates, "EsaPredictedAp":eap,"Esapredictedf10":ef10,"Noaa_predicted_ap":ap,"Noaa_predicted_f10":f10,"Celestrak_predicted_ap":ceap ,	"Celestrak_predicted_f10":cef10,
          "Gfz_Ap":empty_list,	"Gfz_f10":empty_list,	"Esa_Ap":empty_list	,"Esa_f10":empty_list,	"Celestrak_Ap":empty_list,	"Celestrak_f10":empty_list}
    wdf=pd.DataFrame(dict)
       # Count the current number of sheets
    today=datetime.today().strftime("%d-%m-%y")
    new_sheet_name = f'Sheet_{today}'
    # Use ExcelWriter with the 'openpyxl' engine to append the new sheet
    with pd.ExcelWriter(path, engine='openpyxl', mode='a') as writer:
        # Write the DataFrame to the new sheet
        wdf.to_excel(writer, sheet_name=new_sheet_name, index=False)

    ## Updating the present day observed value of Ap and F10 from Celestrak, GFZ and ESA Solmag
    xls = pd.ExcelFile(path)
    all_sheets = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}

    # Standardizing the date format
    date_format="%d/%m/%Y"
    gfz = gfz_data()
    gfz_date = datetime.strptime(gfz.iloc[29], date_format).strftime(date_format)
    esa = esa_data()
    date_object1 = datetime.strptime(esa["#d/mm/yyyy"].iloc[0], "%d/%m/%Y")
    esa_date = date_object1.strftime("%d/%m/%Y")
    # # Process each sheet
    with pd.ExcelWriter(path, engine='openpyxl', mode='a') as writer:
        for key, value in all_sheets.items():
            df = value
            # Updating with the GFZ observed values
            pos = df[df["Date"] == gfz_date].index
            if not pos.empty:
                index = pos[0]
                df.loc[index, "Gfz_Ap"] = gfz["Ap"]
                df.loc[index, "Gfz_f10"] = gfz['F10.7obs']

            # Updating with the ESA observed values
            pos = df[df["Date"] == esa_date].index
            if not pos.empty:
                index = pos[0]
                df.loc[index, "Esa_Ap"] = esa["Ap"].iloc[0]
                df.loc[index, "Esa_f10"] = esa["F10"].iloc[0]

            pos = df[df["Date"] == today_ctrak[0]].index
            if not pos.empty:
                index = pos[0]
                df.loc[index, "Celestrak_Ap"] = float(today_ctrak[1])
                df.loc[index, "Celestrak_f10"] = float(today_ctrak[2])

    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        for sheet_name, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

updateExcel()
