import socket
from DnsPAcket import *
import random
# Static
server_ip = 5555
server_adress = "127.0.0.1"
bufferSize = 1024


serverAddressPort   = (server_adress, server_ip)

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

packet = DnsPAcket()
query_info ="example.com.;MX"
msg = packet.str(str(random.randint(0,65535)),"Q","0","0","0","0",query_info,"0","0","0")


# Send to server using created UDP socket
UDPClientSocket.sendto(msg.encode(), serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)
