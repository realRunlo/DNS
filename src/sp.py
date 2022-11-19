import socket
from threading import Thread
import sys
from parsers import *
from DnsPacket import *
import json

def zone_transfer_handler(connection,adress,db):
    print("sp zone transfer handler")
    db_total_entries = 0
    running = True

    while running:

        msg = connection.recv(1024)

        msg_decoded = msg.decode('utf-8')
        print(msg_decoded)

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

def query_service():
    bufferSize = 1024
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    UDPServerSocket.bind(("127.0.0.1", 5555))


    while(True):

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        thread = Thread(target=query_handler,args=(address,message,UDPServerSocket,db))
        thread.start()

def zone_transfer_sevice():
    address = "127.0.0.1"
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
    print("------------SP----------------")
    # Leitura do ficheiro de configuração
    configs = Configuration()
    configs.parse_from_file(args[0])
    # Leitura do ficheiro com a lista dos servidores de topo
    sdts = SdtServers()
    sdts.parse_from_file(args[1])
    #Leitura com ficheiro de base de dados
    db = Database()
    db.parse_from_file(args[2])



    thread1 = Thread(target=zone_transfer_sevice)
    thread2 = Thread(target=query_service)
    thread1.start()
    thread2.start()
