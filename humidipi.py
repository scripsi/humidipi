import paho.mqtt.client as mqtt
from configparser import ConfigParser
import signal
import math
from pathlib import Path
import ledshim

ini = ConfigParser()
ini_file = Path.home() / "scripsi" / "humidipi.ini"
ini.read(ini_file)

air_temp = 20.0
wall_temp = 20.0
dew_temp = 20.0
air_humidity = 50.0

ledshim.set_clear_on_exit()
ledshim.set_brightness(0.3)
ledshim.set_all(255,255,0,0.4)
ledshim.show()

def term_handler():
    ledshim.clear()
    ledshim.show()

def calculate_dew_point():
    global air_temp, air_humidity, dew_temp
    print("calculate_dew_point() called")
    # Magnus formula from https://en.wikipedia.org/wiki/Dew_point#Calculating_the_dew_point
    b = 17.625
    c = 243.04
    gamma = math.log(air_humidity/100) + ((b * air_temp)/(c + air_temp))
    dew_temp = (c * gamma) / (b - gamma)
    print(f"Dew Temperature: {dew_temp:.1f} C")

def update_display():
    ledshim.clear()
    for i in range(min(max(round(dew_temp),0),ledshim.NUM_PIXELS)):
        if i < wall_temp:
            ledshim.set_pixel(i, 0, 255, 0)
        else:
            ledshim.set_pixel(i, 255, 0, 0)
    ledshim.set_pixel(round(wall_temp), 0, 0, 255)
    ledshim.show()

def on_connect(client, userdata, flags, reason_code):
    print('Connected with result code ' + str(reason_code))
    if reason_code == 0:
        ledshim.set_all(255,0,255,0.4)
        ledshim.show()
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
                update_display()
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
                update_display()
            print(f"Air Humidity: {air_humidity:.1f} %")

signal.signal(signal.SIGTERM,term_handler)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username=ini['mqtt']['username'], password=ini['mqtt']['password'])

client.connect(ini['mqtt']['server'], int(ini['mqtt']['port']), 60)

client.loop_forever()
