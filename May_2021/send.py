import socket
import random

def send_tone(value):
    # home
    # UDP_IP = "10.0.0.166"
    # at school
    UDP_IP = "129.64.50.48"
    #when on phone
    #UDP_IP = "172.20.10.8"
    UDP_PORT = 5005

    MESSAGE = value
    print(int.from_bytes(value, 'big'))

    print("UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)
    print("message:", MESSAGE)

    sock = socket.socket(socket.AF_INET, #internet
                        socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    
# value = random.randint(0,4)
value = 4
send_tone(value.to_bytes(2, 'big'))
