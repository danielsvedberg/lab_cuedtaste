
import socket

UDP_IP = "129.64.50.48"
UDP_PORT = 5005

# make into a function to make message = a passed parameter (tone values)
MESSAGE = "2"

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, #internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))