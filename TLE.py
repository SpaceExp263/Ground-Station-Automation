"""
Program to calculate TLE 4,6 and 8 minutes earlier than current time for a particular satellite
"""

import requests
import pandas as pd
from datetime import datetime,timedelta
import math
from skyfield.api import Topos, EarthSatellite, load
import ephem


def calculate_checksum(line):
    """
    Calculates the checksum for a given TLE line.
    """
    checksum = 0
    for char in line:
        if char.isdigit():
            checksum += int(char)
        elif char == '-':
            checksum += 1
    return checksum % 10

def fractionalday(timestamp_str,min):
    timestamp = datetime.fromisoformat(timestamp_str)
    # Extract hours, minutes, seconds, and microseconds
    newtimestamp=timestamp-timedelta(minutes=min)
    hours = newtimestamp.hour
    minutes = newtimestamp.minute
    seconds = newtimestamp.second
    microseconds = newtimestamp.microsecond

    # Calculate the total seconds in the day
    total_seconds_in_day = 24 * 60 * 60

    # Calculate the fractional part of the day
    fractional_day = (hours * 60 * 60 + minutes * 60 + seconds + microseconds / 1_000_000) / total_seconds_in_day
    rounded_fractional_day = round(fractional_day, 8)
    fractional_day=str(rounded_fractional_day)[1:]
    return fractional_day

def ddot(number):
    # Convert the number to scientific notation string
    if number==0.0:
        result="00000-0"
    else:
        exponent = int(math.floor(math.log10(abs(number))))
        # Adjust the exponent to make the coefficient 5 digits long
        adjusted_exponent = exponent - 4
        # Calculate the new coefficient
        adjusted_coefficient = int(number / (10 ** adjusted_exponent))
        # Ensure the coefficient is rounded to 5 digits
        adjusted_coefficient = round(adjusted_coefficient, 5)
        # Construct the final representation
        result = f"{adjusted_coefficient}{adjusted_exponent+5}"
    return result

def format_tle(row,min):
    """
    This function takes a pandas Series of satellite data and formats it into a TLE string.
    """
    formatted_object_id = row['OBJECT_ID'][:4][2:] + row['OBJECT_ID'][5:].replace('-', '')
    # Format the MEAN_MOTION_DOT, checking if it's in scientific notation
    mean_motion_dot = row['MEAN_MOTION_DOT']
    #print(row['MEAN_MOTION_DOT'])
    if 'e' in f"{mean_motion_dot}":
        formatted_mean_motion_dot = f"{mean_motion_dot:.8f}"  # Convert to decimal with full precision
    else:
        formatted_mean_motion_dot = f".{str(mean_motion_dot)[2:]}"  # Use existing format

    exponent = 0
    sign='+'
    bstar=row['BSTAR']
    if bstar!=0:
        if bstar<0:
            bstar*=-1
            sign='-'
        while bstar < 10000 :
            bstar *= 10
            exponent -= 1  # Decrement exponent as we are effectively dividing by 10

    eccentricity=str(row['ECCENTRICITY'])
    epoch=fractionalday(str(row['EPOCH']),min)
    original_datetime = datetime.strptime(row["EPOCH"], "%Y-%m-%dT%H:%M:%S.%f")
    day_of_year = original_datetime.timetuple().tm_yday
    mddot=ddot(row["MEAN_MOTION_DDOT"])
    # Format the first line of TLE
    line1 = f"1 {int(row['NORAD_CAT_ID']):05d}U {formatted_object_id}   {row['EPOCH'][2:4]}{day_of_year:03d}{epoch}  {formatted_mean_motion_dot}  {mddot}  {sign}{int(bstar):05d}{exponent+5:+d} 0 {int(row['ELEMENT_SET_NO']):4d}"
    # Format the second line of TLE
    line2 = f"2 {int(row['NORAD_CAT_ID']):05d}  {row['INCLINATION']:.4f}  {row['RA_OF_ASC_NODE']:.4f} {eccentricity[2:]} {row['ARG_OF_PERICENTER']:.4f} {row['MEAN_ANOMALY']:.4f} {row['MEAN_MOTION']:.8f}{row['REV_AT_EPOCH']}"

    # Calculate checksum for each line
    checksum1 = calculate_checksum(line1)
    checksum2 = calculate_checksum(line2)
    # Append checksum to each line
    line1 += str(checksum1)
    line2 += str(checksum2)
    tle=[line1,line2]
    return tle

def data_collect(norad_cat_id):
    url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json"
    response = requests.get(url)
    if response.status_code == 200:
        response = response.json()
    else:
        print("Request Status :", response.status_code, "\nRequest unable to process")
        return  # Exit the main function if the request fails

    df = pd.DataFrame.from_dict(response)
    satellite_data = df[df['NORAD_CAT_ID'] == norad_cat_id]
    tle=[]
    # Check if any data was found
    if not satellite_data.empty:
        # Retrieve the TLE from the first row
        minutes=[0,4,6,8]
        for i in minutes:
            tle.append(format_tle(satellite_data.iloc[0],i))
    return tle,satellite_data["OBJECT_NAME"].iloc[0]

def satdata(norad_cat_id,num_of_passes):
    # Speed of light in meters per second
    c = 299792458
    # Transmitted frequency (example: 437.5 MHz for a CubeSat)
    f = 437.5e6  # Convert MHz to Hz
    line,name=data_collect(norad_cat_id)
    print(name)
    data=line[0]
    print(data)
    observer = ephem.Observer()
    observer.lat = '1.3568'  # Example: Latitude of Satellite Research Centre, NTU, in degrees
    observer.lon = '103.692'  # Example: Longitude of Satellite Research Centre, NTU,, in degrees
    observer.elevation = 23
    satellite=ephem.readtle(name,data[0],data[1])
    observer.date = ephem.now()  # Set the observation date to now
    satellite.compute(observer)

    n_passes = num_of_passes
    passes = []  # List to store pass details
    dopplershift=[]
    for _ in range(n_passes):
        # Compute the next pass of the satellite over the observer's location
        next_pass = observer.next_pass(satellite)
        passes.append(next_pass)

        # Update the observer's time to just after the end of the current pass
        observer.date = next_pass[4] + ephem.minute  # Set time just after the satellite sets

        # Reset the satellite's details to ensure accuracy in the next computation
        satellite.compute(observer)
        v = satellite.range_velocity  # Positive if moving away, negative if moving towards
        # Calculate the observed frequency
        f_observed = f * (c + v) / c

        # Print the Doppler shift and the observed frequency
        doppler_shift = f_observed - f
        dopplershift.append(doppler_shift)

    passData={}
    for i, pass_detail in enumerate(passes):
        rise_time, rise_azimuth, max_alt_time, max_alt, set_time, set_azimuth = pass_detail

        passData[f"Pass {i + 1}"] = {
            "Rise azimuth": str(rise_azimuth),
            "Rise Time": str(rise_time),
            "Max altitude": str(max_alt),
            "Set azimuth": str(set_azimuth),
            "Doppler Shift": dopplershift[i]
        }

    return passData


def main():
    list, name = data_collect(57482)
    ts = load.timescale()
    for i in list:
        satellite = EarthSatellite(i[0], i[1], name, ts)
        print(satellite, "\n TLE: ", i)


if __name__ == "__main__":
     main()
