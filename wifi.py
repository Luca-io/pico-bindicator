# Connects the Pico to wifi

import network
import socket
from time import sleep
import machine
import rp2
import sys

ssid = 'NETWORK NAME'
pwd = 'NETWORK PASSWORD'

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, pwd)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(0.5)
    print('Connected to wifi')
