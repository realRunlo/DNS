import socket
from DnsPacket import *
import random
# Static
server_ip = 5555
server_adress = "127.0.0.1"
bufferSize = 1024


serverAddressPort   = (server_adress, server_ip)

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

id = random.randint(0,65535)

packet = DnsConcisoPacket()
packet.request(id,"Q","example.com.","MX")

msg = packet.str()
pmsg = packet.prettyStr()
print("Query enviada do cliente")
print(pmsg)


# Send to server using created UDP socket
UDPClientSocket.sendto(msg.encode(),serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

print("Resposta do SP")
packet.fromStr(msgFromServer[0].decode())
print(packet.prettyStr())
