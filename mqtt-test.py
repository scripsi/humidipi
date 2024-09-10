import paho.mqtt.client as mqtt
from configparser import ConfigParser
import time
import math
from pathlib import Path

ini = ConfigParser()
ini_file = Path.home() / "scripsi" / "humidipi.ini"
ini.read(ini_file)

air_temp = 20.0
wall_temp = 20.0
dew_temp = 20.0
air_humidity = 50.0
display_string = "-" * 28
display_pixels = list(display_string)

def calculate_dew_point():
    global air_temp, air_humidity, dew_temp
    print("calculate_dew_point() called")
    # Magnus formula from https://en.wikipedia.org/wiki/Dew_point#Calculating_the_dew_point
    b = 17.625
    c = 243.04
    gamma = math.log(air_humidity/100) + ((b * air_temp)/(c + air_temp))
    dew_temp = (c * gamma) / (b - gamma)
    print(f"Dew Temperature: {dew_temp:.1f} C")

def update_display_string():
    global display_pixels, display_string
    display_pixels = list(display_string)
    for i in range(round(dew_temp)):
        if i < wall_temp:
            display_pixels[i] = "O"
        else:
            display_pixels[i] = "*"
    display_pixels[round(wall_temp)] = "+"
    print("".join(display_pixels))

def on_connect(client, userdata, flags, reason_code):
    print('Connected with result code ' + str(reason_code))

    client.subscribe(ini['mqtt']['topic'])

def on_message(client, userdata, msg):

    global air_temp, wall_temp, air_humidity
    sensor = msg.topic.split("/")[-1]
    if sensor == "airtemp":
            new_air_temp = float(msg.payload)
            if air_temp != new_air_temp:
                print("Air Temperature changed!")
                air_temp = new_air_temp
                calculate_dew_point()
                update_display_string()
            print(f"Air Temperature: {air_temp:.1f} C")
    elif sensor == "walltemp":
            wall_temp = float(msg.payload)
            print(f"Wall Temperature: {wall_temp:.1f} C")
    elif sensor == "humidity":
            new_air_humidity = float(msg.payload)
            if air_humidity != new_air_humidity:
                print("Air Humidity changed!")
                air_humidity = new_air_humidity
                calculate_dew_point()
                update_display_string()
            print(f"Air Humidity: {air_humidity:.1f} %")
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username=ini['mqtt']['username'], password=ini['mqtt']['password'])

client.connect(ini['mqtt']['server'], int(ini['mqtt']['port']), 60)

client.loop_forever()
