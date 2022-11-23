import socket
from DnsPacket import *
import sys
import random
# Static
default_port = 5555
bufferSize = 1024

# ip name type
# OU
# ip:Por name type
print("------------CLI----------------")
args = sys.argv[1:]


adress_port = args[0].split(':')

if len(adress_port)==2:
    serverAddressPort   = (adress_port[0], adress_port[1])
else:
    serverAddressPort   = (adress_port[0], default_port)

name = args[1]
type_of_value = args[2]



# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

id = random.randint(0,65535)

packet = DnsConcisoPacket()
packet.request(id,"Q",name,type_of_value)


print("Query enviada:")
print(packet.prettyStr()) # prettyStr modo de apresentar no terminal


msg = packet.str()
# Send to server using created UDP socket
UDPClientSocket.sendto(msg.encode(),serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

print("Resposta:")
packet.fromStr(msgFromServer[0].decode())
print(packet.prettyStr())
