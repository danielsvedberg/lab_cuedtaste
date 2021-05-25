
"""
Author: emmabarash
This program recieves values from send_tone_value.py on the cue RPi
"""

import socket

def get_value(int):
        return int

UDP_IP = "129.64.50.48"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # internet
                     socket.SOCK_DGRAM) #UDP

sock.bind((UDP_IP, UDP_PORT))

while True:
        data, addr = sock.recvfrom(1024) #buffer size is 1024 bytes
        # send this to function that initiates tone/replace keyboard values
        print"recieved message:", int(data)
        get_value(int(data))
        
        