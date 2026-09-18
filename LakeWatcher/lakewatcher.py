#! /usr/bin/python3

import requests
import urllib.request
import inspect
from datetime import datetime, timedelta
from paho.mqtt import publish as publish
import json
import syslog
import os
import schedule
import time

water_depth_column = '177214_00062'
water_temp_top_column = '177216_00010'
water_temp_bottom_column = '177218_00010'
CFG_PATH = '/etc/default/weatherwatcher/config.json'
host = ''
token = ''

def read_config() -> None:
    """Reads configuration from a JSON file to get the host and token."""
    global host, token
    if os.path.exists(CFG_PATH):
        with open(CFG_PATH) as json_file:
            cfg = json.load(json_file)
            print(cfg)
            if 'THINGSBOARD_HOST' in cfg:
                host = cfg['THINGSBOARD_HOST']
            if 'ACCESS_TOKEN' in cfg:
                token = cfg['ACCESS_TOKEN']

def ctof(temp: float) -> float:
    """Converts Celsius to Fahrenheit."""
    try:
        return (float(temp) * 9/5) + 32
    except (TypeError, ValueError):
        return 0.0

def fetch_lake_data() -> dict | None:
    """Fetches lake data from USGS and parses it to JSON."""
    water_depth_position = -1
    water_temp_top_position = -1
    water_temp_bottom_position = -1
    today = datetime.strftime(datetime.now(), '%Y-%m-%d')
    yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    url = f'https://waterdata.usgs.gov/sc/nwis/uv?cb_00010=on&cb_00010=on&cb_00035=on&cb_00036=on&cb_00062=on&cb_00300=on&cb_00300=on&format=rdb&site_no=02168500&period=&begin_date={yesterday}&end_date={today}'
    response = requests.get(url)
    print(response.status_code)
    if response.status_code != 200:
        syslog.syslog(syslog.LOG_ERR, f"{inspect.currentframe().f_code.co_name} received {response.status_code}:{response.reason}")
        return None
    else:
        water_depth_position = water_temp_top_position = water_temp_bottom_position = 0
        for line in response.text.split('\n'):
            if line[0:len('agency_cd')] == 'agency_cd':
                columns = line.split('\t')
                column_cnt = 0
                for column in columns:
                    if column == water_depth_column:
                        water_depth_position = column_cnt
                    elif column == water_temp_top_column:
                        water_temp_top_position = column_cnt
                    elif column == water_temp_bottom_column:
                        water_temp_bottom_position = column_cnt
                    column_cnt += 1
                break
        lastline = response.text.split('\n')[-2:-1]
        fields = lastline[0].split('\t')
        water_depth = float(fields[water_depth_position]) if water_depth_position > 0 else 0.0
        water_temp_top = ctof(fields[water_temp_top_position]) if water_temp_top_position > 0 else 0.0
        water_temp_bottom = ctof(fields[water_temp_bottom_position]) if water_temp_bottom_position > 0 else 0.0
        lake_data_json = {'temp_top': water_temp_top, 'temp_bottom': water_temp_bottom, 'water_level': water_depth}
        return lake_data_json


def fetch_weather(lat: str, long: str, key: str) -> dict | None:
    """Fetches weather data from the OpenWeatherMap API."""
    print(f'Fetching forecast for lat {lat} long {long}')  # Press Ctrl+F8 to toggle the breakpoint.
    r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={key}&units=imperial")
    print(r.status_code)
    print(r.text)
    if r.status_code != 200:
        print(f"Error {r.status_code} fetching weather")
        return None
    else:
        data = json.loads(r.text)
        weather_data = {'temp': data["main"]["temp"], 'pressure': data["main"]["pressure"],
                        'humidity': data["main"]["humidity"], 'windspeed': data["wind"]["speed"],
                        'winddeg': data["wind"]["deg"]}
        return weather_data


def publish_data(source: str, data: dict | None):
    if data is not None:
        try:
            publish.single('v1/devices/me/telemetry', json.dumps(data), hostname=host,
                           auth={'username': token, 'password': ''})
            print(f"[{datetime.now()}] Successfully published {source} data: {data}")
        except ConnectionRefusedError:
            syslog.syslog(syslog.LOG_ERR, f"{source} received ConnectionRefusedError")
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,
                          f"{source} received unexpected Exception {type(e).__name__}")
    else:
        syslog.syslog(syslog.LOG_ERR, f"{source} received None data")

def lake_data_job() -> None:
    """Job that fetches data and publishes it to ThingsBoard."""
    data = fetch_lake_data()
    publish_data(source='LakeWatcher', data= data)



def weather_data_job() -> None:
    """Job that fetches weather data and publishes it to ThingsBoard."""
    data = fetch_weather(lat="34.034914", long="-81.271652", key="e2a03fbc86a197fedee6c8777c2cf149")
    publish_data(source='WeatherWatcher', data= data)

if __name__ == '__main__':
    read_config()
    syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)
    
    print("Starting LakeWatcher...")
    
    # Run once immediately
    lake_data_job()
    weather_data_job()
    
    # Schedule to run every 6 hours (4 times a day)
    schedule.every(6).hours.do(lake_data_job)
    
    # Schedule to run every 15 minutes
    schedule.every(15).minutes.do(weather_data_job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
