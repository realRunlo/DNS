import socket
from threading import Thread
import sys
from parsers import *
from DnsPacket import *
from requests import get
import json

def zone_transfer_handler(connection,adress,db):
    print("sp zone transfer handler")
    db_total_entries = 0
    running = True

    while running:

        msg = connection.recv(1024)

        msg_decoded = msg.decode('utf-8')
        print(msg_decoded)
        db.print()
        if msg_decoded=="serial":
            # Responde ao pedido do SS enviado o número de serie da db
            connection.sendall(db.soaserial['value'].encode('utf-8'))
        elif msg_decoded=="get":
            # SP envia o núemro de entradas da sua bd
            db_total_entries = db.size()
            connection.sendall(str(db_total_entries).encode('utf-8'))
        elif msg_decoded=="ok":
            # SP envia linha a linha a sua bd
            counter = 1
            db_list = db.to_list()
            while counter<=db_total_entries:
                for entry in db_list:
                    send_entry_msg = str(counter) + ";" + json.dumps(entry) + ";"
                    # Adicionar padding
                    send_entry_msg = send_entry_msg.ljust(200,"0")
                    connection.sendall(send_entry_msg.encode('utf-8'))
                    counter += 1
                # Depois de enviar todas as entradas da base de dados termina a conexão
                connection.close()
                print("Transferência de zona terminada")
                running = False
        elif msg_decoded=="abandon":
            connection.close()
            running = False

def query_handler(address,message,UDPServerSocket,db):
    recv_packet = DnsConcisoPacket()
    recv_packet.fromStr(message.decode())

    print("Query recebida:")
    print(recv_packet.prettyStr())

    has_domain = db.has_domain(recv_packet.name)
    # Resposta com aquele nome de dominio e tipo na base de dados
    response_values = db.get_response_values(recv_packet.name,recv_packet.value_type)
    # Resposta com servidores autoritativos
    auth_values = db.get_auth_values(recv_packet.name)
    # Resposta com valores exra
    extra_values = db.get_extra_values(response_values,auth_values)

    if has_domain and len(response_values) > 0:
        #Response code 0
        response_packet = recv_packet.response("A",0,response_values,auth_values,extra_values)
    elif has_domain:
        #Response code 1
        response_packet = recv_packet.response("A",1,response_values,auth_values,extra_values)
    elif not has_domain:
        #Response code 2
        response_packet = recv_packet.response("A",2,response_values,auth_values,extra_values)
    else:
        #Response code 3
        response_packet = recv_packet.response("A",3,response_values,auth_values,extra_values)


    msg = response_packet.str()
    UDPServerSocket.sendto(msg.encode(), address)

def query_service():
    bufferSize = 1024
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    my_address = db.a[0]["value"]
    print(my_address)
    # Bind to address and ip
    UDPServerSocket.bind((my_address,5555))


    while(True):

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        thread = Thread(target=query_handler,args=(address,message,UDPServerSocket,db))
        thread.start()

def zone_transfer_sevice():
    address = db.a[0]["value"]
    port = 6000
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    serversocket.bind((address,port))
    # become a server socket
    serversocket.listen()

    # À escuta por pedidos de transferência de zona
    while True:
        # accept connections from outside
        (connection, address) = serversocket.accept()
        # now do something with the clientsocket
        # in this case, we'll pretend this is a threaded server
        thread = Thread(target=zone_transfer_handler,args=(connection,address,db))
        thread.start()

    pass



if __name__ == '__main__':

    args = sys.argv[1:]
    # configFile
    print("------------SP----------------")
    # Leitura do ficheiro de configuração
    configs = Configuration()
    configs.parse_from_file(args[0])


    if len(configs.db) > 1:
        # fazer uma lista de dicionarios dominio-db_correspondente
        # este é o caso em que é um sp de um dominio de topo ou seja tem mais que uma base de dados
        pass
    else:
        db = Database()
        db.parse_from_file(configs.db[0]['filepath'])

    # Leitura do ficheiro com a lista dos servidores de topo
    sdts = SdtServers()
    sdts.parse_from_file(configs.st['filepath'])


    thread1 = Thread(target=zone_transfer_sevice)
    thread2 = Thread(target=query_service)
    thread1.start()
    thread2.start()
