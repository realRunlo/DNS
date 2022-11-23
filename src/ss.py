import socket
import time
import sys
import json
import re
from parsers import *
from threading import Thread





def query_handler(adress,message,UDPServerSocket,db):
    recv_packet = DnsConcisoPacket()
    print(message)
    recv_packet.fromStr(message.decode())

    print(recv_packet.name)
    print(recv_packet.value_type)
    response_values = db.get_response_values(recv_packet.name,recv_packet.value_type)
    auth_values = db.get_auth_values(recv_packet.name)
    extra_values = db.get_extra_values(response_values,auth_values)

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
    pass


def zone_transfer_handler(db,domain):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 6000))

    request_db_serial_msg = "serial"
    # Envia pedido para saber número de série da db do SP
    s.sendall(request_db_serial_msg.encode('utf-8'))

    print("enviei")
    # Recebe número de série da db do SP
    db_serial = s.recv(1024)

    total_entries = 0
    # Se a versão for diferente da que está no SP ou o SS ainda não tiver a base de dados carregada
    if db.soaserial=={} or db_serial.decode('utf-8') != db.soaserial['value']:
        #  SS envia  o nome completo do domínio para a qual quer receber uma cópia da base de dados do SP
        s.sendall("get".encode('utf-8'))
        total_entries = s.recv(1024)
        total_entries = int(total_entries.decode())

        if total_entries<=65535:
            # SS aceita o número de entradas
            s.sendall("ok".encode('utf-8'))

            last_entry = 0
            while total_entries>0:
                entrie_msg = s.recv(200)
                entrie_msg = entrie_msg.decode('utf-8')

                fields = entrie_msg.split(";")

                entry_number = int(fields[0])
                entry = json.loads(fields[1])

                type = entry['type']
                del entry['type']

                # Adciona entrada à base de dados
                db.add_entry(type,entry)
                total_entries -= 1


            db.print()
            # SS já tem a base de dados em memória, abandona coneção
            s.close()
            print("Transferência de zona terminada")


    else:
        s.sendall("abandon".encode('utf-8'))
        s.close()



def query_service():
    bufferSize = 1024
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    my_address = socket.gethostbyname(socket.gethostname())
    print(my_address)
    # Bind to address and ip
    UDPServerSocket.bind((my_address, 5556))

    while(True):

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        thread = Thread(target=query_handler,args=(address,message,UDPServerSocket,db))
        thread.start()


def zone_transfer_sevice():

    while True:

        thread3 = Thread(target=zone_transfer_handler,args=(db,configs.sp[0]["dominio"]))
        thread3.start()
        thread3.join()

        time.sleep(int(db.soarefresh["value"]))


if __name__ == '__main__':

    args = sys.argv[1:]
    # configFile
    print("------------SS----------------")

    # Leitura do ficheiro de configuração
    configs = Configuration()
    configs.parse_from_file(args[0])

    # Leitura do ficheiro com a lista dos servidores de topo
    #sdts = SdtServers()
    #sdts.parse_from_file(configs.st['filepath'])

    db = Database()


    thread1 = Thread(target=zone_transfer_sevice)
    thread2 = Thread(target=query_service)
    thread1.start()
    thread2.start()
