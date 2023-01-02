import socket
from DnsPacket import *
import sys
import random
import datetime
from logsys import *

# Static
default_port = 5555
bufferSize = 1024
logFilePath = "server/Logs/all.txt"
# shy | debug
logMode = "debug"

# ip name type
# OU
# ip:Por name type
print("------------CLI----------------")

args = sys.argv[1:]
address = args[0].split(':')

if len(address)==2:
    serverAddress   = (address[0], address[1])
else:
    serverAddress   = (address[0], default_port)

name = args[1]
type_of_value = args[2]

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Create Log Object
log = Log(logFilePath, logMode)

# Create PDU
id = random.randint(0,65535)
packet = DnsConcisoPacket()
packet.request(id,"Q",name,type_of_value)

# Send query to server using created UDP socket
message = packet.str()
UDPClientSocket.sendto(message.encode(),serverAddress)
time = datetime.datetime.now()
log.logEntry(time, "QE", ipLog(address[0], default_port), message)

# Receive answer from server
msgFromServer = UDPClientSocket.recvfrom(bufferSize)
time = datetime.datetime.now()
log.logEntry(time, "RR", ipLog(address[0], default_port), msgFromServer[0].decode())

packet.fromStr(msgFromServer[0].decode())

# For Optional understandable print
#print(packet.prettyStr())
