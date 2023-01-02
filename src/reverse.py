import socket
from threading import Thread
import sys
from parsers import *
from DnsPacket import *
from requests import get
import json
import datetime
from logsys import *
import re

def query_handler(address,message,UDPServerSocket, sdts, log):
    bufferSize = 1024
    # Log Query
    time = datetime.datetime.now()
    log.logEntry(time, "QR", ipLog(address[0], address[1]), message.decode())

    # Check Cache

    # Create secondary socket
    SecondServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    SecondServerSocket.bind((my_address, 5554))

    # Send to ST
    SecondServerSocket.sendto(message, (sdts.table[0][0], 5555))

    # Receive from ST
    bytesAddressPair = SecondServerSocket.recvfrom(bufferSize)

    recv_packet = DnsConcisoPacket()
    recv_packet.fromStr(bytesAddressPair[0].decode())

    new_ip = recv_packet.extra_vals.split(" ")

    counter = 0
    while(new_ip[0] != "" and counter < 2 and len(new_ip) < 5):
        SecondServerSocket.sendto(message, (new_ip[2], 5555))
        bytesAddressPair = SecondServerSocket.recvfrom(bufferSize)

        recv_packet.fromStr(bytesAddressPair[0].decode())
        new_ip = recv_packet.extra_vals.split(" ")
        counter += 1

    # Send response to client
    UDPServerSocket.sendto(bytesAddressPair[0], address)

    # Log Resposta à query enviada
    time = datetime.datetime.now()
    log.logEntry(time, "RE", ipLog(address[0], address[1]), recv_packet.str())

def query_service():
    bufferSize = 1024
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    print(my_address)

    # Bind to address and ip
    UDPServerSocket.bind((my_address,5555))

    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        recv_packet = DnsConcisoPacket()
        recv_packet.fromStr(message.decode())

        thread = Thread(target=query_handler,args=(address,message,UDPServerSocket, sdts, log))
        thread.start()



if __name__ == '__main__':
    args = sys.argv[1:]

    print("------------SR----------------")

    # Leitura do ficheiro de configuração
    configs = Configuration()
    configs.parse_from_file(args[0])

    # Own IP
    my_address = args[1]

    # Inicializa o Log
    log = Log(configs.lg[0]['filepath'], "shy")

    # Leitura do ficheiro com a lista dos servidores de topo
    sdts = SdtServers()
    sdts.parse_from_file(configs.st['filepath'])

    # Log ST Read
    time = datetime.datetime.now()
    log.logEntry(time, "EV", "127.0.0.1", evLogData("st-file-read", configs.st['filepath']))

    # Inicialização do serviço de Query
    thread1 = Thread(target=query_service)
    thread1.start()
