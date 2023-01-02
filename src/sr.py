import socket
from threading import Thread
import sys
from parsers import *
from DnsPacket import *
from requests import get
from cache import *
import json
import datetime
from logsys import *
import re

# shy | debug
logMode = "debug"
# True | False
recursive = False

def query_handler(address,message,UDPServerSocket, sdts, cache, log):
    bufferSize = 1024
    recv_packet = DnsConcisoPacket()
    recv_packet.fromStr(message.decode())
    # Log Query
    time = datetime.datetime.now()
    log.logEntry(time, "QR", ipLog(address[0], address[1]), message.decode())

    domain = recv_packet.name

    # Checking Cache
    # Resposta com aquele nome de dominio e tipo na base de dados
    response_values = cache.get_response_values(recv_packet.name,recv_packet.value_type)
    # Resposta com servidores autoritativos
    auth_values = cache.get_auth_values(domain)
    # Resposta com valores exra
    extra_values = cache.get_extra_values(response_values, auth_values)

    if len(response_values) > 0:
        # Response code 0: Nenhum erro, o sistema tem informação direta sobre a query
        response_packet = recv_packet.response("A",0,response_values,auth_values,extra_values)

        # Send response to client
        msg = response_packet.str()
        UDPServerSocket.sendto(msg.encode(), address)
    else:
        # Create secondary socket
        SecondServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        SecondServerSocket.bind(('', 5554))

        # If recursive mode is activated inster R into flag
        if recursive:
            message = message.decode()
            index = message.find(',')
            message = message[:index+2] + "R" + message[index+2:]
            message = message.encode()

        # Send to ST
        SecondServerSocket.sendto(message, (sdts.table[0][0], 5555))

        # Log Query
        time = datetime.datetime.now()
        log.logEntry(time, "QE", ipLog(sdts.table[0][0], 5555), message.decode())

        # Receive from ST
        bytesAddressPair = SecondServerSocket.recvfrom(bufferSize)

        # Log Query
        time = datetime.datetime.now()
        log.logEntry(time, "QR", ipLog(sdts.table[0][0], 5555), message.decode())

        recv_packet.fromStr(bytesAddressPair[0].decode())

        if not recursive:
            new_ip = recv_packet.extra_vals.split(" ")

            counter = 0
            while(new_ip[0] != "" and counter < 2 and len(new_ip) < 5):
                SecondServerSocket.sendto(message, (new_ip[2], 5555))
                bytesAddressPair = SecondServerSocket.recvfrom(bufferSize)

                # Log Query
                time = datetime.datetime.now()
                log.logEntry(time, "QE", ipLog(new_ip[2], 5555), message.decode())

                recv_packet.fromStr(bytesAddressPair[0].decode())

                # Log Query
                time = datetime.datetime.now()
                log.logEntry(time, "QR", ipLog(new_ip[2], 5555), message.decode())

                new_ip = recv_packet.extra_vals.split(" ")
                counter += 1
        # Send response to client
        UDPServerSocket.sendto(bytesAddressPair[0], address)

        # Add to cache
        if (recv_packet.response_code == 0):
            cache.cache_packet(recv_packet)



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

        thread = Thread(target=query_handler,args=(address,message,UDPServerSocket, sdts, cache, log))
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
    log = Log(configs.lg[0]['filepath'], logMode)

    # Leitura do ficheiro com a lista dos servidores de topo
    sdts = SdtServers()
    sdts.parse_from_file(configs.st['filepath'])

    cache = Cache()

    # Log ST Read
    time = datetime.datetime.now()
    log.logEntry(time, "EV", "127.0.0.1", evLogData("st-file-read", configs.st['filepath']))

    # Inicialização do serviço de Query
    thread1 = Thread(target=query_service)
    thread1.start()
