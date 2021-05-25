from send_tone_value import UDP_IP
import socket
import random

def send_tone(value):
    #UDP_IP = "129.64.50.48"
    #when on phone
    UDP_IP = "172.20.10.8"
    UDP_PORT = 5005

    MESSAGE = value

    print "UDP target IP:", UDP_IP
    print "UDP target port:", UDP_PORT
    print "message:", MESSAGE

    sock = socket.socket(socket.AF_INET, #internet
                        socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    
value = random.randint(0,4)
send_tone(str(value))
