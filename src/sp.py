import socket
from threading import Thread
import sys
from parsers import *
from DnsPacket import *

def query_handler(adress,message,database):
    recv_packet = DnsConcisoPacket()
    print(message)
    recv_packet.fromStr(message.decode())

    print(recv_packet.name)
    print(recv_packet.value_type)
    response_values = database.get_response_values(recv_packet.name,recv_packet.value_type)
    auth_values = database.get_auth_values(recv_packet.name)
    extra_values = database.get_extra_values(response_values,auth_values)
    print("REPONSE")
    for elem in response_values:
        print(elem)
    print("AUTH")
    for elem in auth_values:
        print(elem)
    print("EXTRA")
    for elem in extra_values:
        print(elem)


    response_packet = recv_packet.response("A",response_values,auth_values,extra_values)
    msg = response_packet.str()

    UDPServerSocket.sendto(msg.encode(), address)





if __name__ == '__main__':

    args = sys.argv[1:]

    # Leitura do ficheiro de configuração
    configs = Configuration.parse_from_file(args[0])
    # Leitura do ficheiro com a lista dos servidores de topo
    sdts = SdtServers.parse_from_file(args[1])
    #Leitura com ficheiro de base de dados
    db = Database.parse_from_file(args[2])

    db.print()

    bufferSize = 1024
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    UDPServerSocket.bind(("127.0.0.1", 5555))


    while(True):

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        thread = Thread(target=query_handler,args=(address,message,db))
        thread.start()
