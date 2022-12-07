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

def zone_transfer_handler(connection,address,db,configs,log):
    db_total_entries = 0
    while True:
        # Recebe ZT message
        msg = connection.recv(1024)
        timeStart = datetime.datetime.now()
        msg_decoded = msg.decode('utf-8').split(":")
        msg_decoded_type = msg_decoded[0]
        msg_decoded_data = msg_decoded[1]

        if msg_decoded_type=="serial":
            # Responde ao pedido do SS enviado o número de serie da db
            connection.sendall(db.soaserial['value'].encode('utf-8'))
        elif msg_decoded_type=="domain":
            # SP envia o núemro de entradas da sua bd
            if configs.ss_has_auth(msg_decoded_data,address[0]):
                db_total_entries = db.size()
                entries_response = "entries:" + str(db_total_entries)
                connection.sendall(entries_response.encode('utf-8'))
            else:
                # Mandar um permission denie ou algo do genero
                connection.sendall("error:permission denied:".encode('utf-8'))
        elif msg_decoded_type=="ok":
            # SP envia linha a linha a sua bd
            counter = 1
            db_list = db.to_list()

            # ASK: While com o for e counter? terminaria n vezes a connection caso o for nao faça direito?
            for entry in db_list:
                send_entry_msg = str(counter) + ";" + json.dumps(entry) + ";"
                # Adicionar padding
                send_entry_msg = send_entry_msg.ljust(200,"0")
                connection.sendall(send_entry_msg.encode('utf-8'))
                counter += 1
            # Regista Log
            timeEnd = datetime.datetime.now()
            log.logEntry(timeEnd, "ZT", ipLog(address[0], address[1]), ztLogData("SP", timeStart, timeEnd))
            # Depois de enviar todas as entradas da base de dados termina a conexão
            connection.close()
            break
        elif msg_decoded=="abandon":
            connection.close()
            break
        db.print()

def query_handler(address,message,UDPServerSocket,db, log):
    # Receive Query
    recv_packet = DnsConcisoPacket()
    recv_packet.fromStr(message.decode())

    # Log Query
    time = datetime.datetime.now()
    log.logEntry(time, "QR", ipLog(address[0], address[1]), message.decode())

    # Process Query
    domain = recv_packet.name
    while (not db.has_domain(domain) and domain != "" and "." in domain):
        domain = re.sub(r'^\w*\.', "", domain)

    # Verifica se existe dominio
    has_domain = db.has_domain(domain)
    # Resposta com aquele nome de dominio e tipo na base de dados
    response_values = db.get_response_values(recv_packet.name,recv_packet.value_type)
    # Resposta com servidores autoritativos
    auth_values = db.get_auth_values(domain)
    # Resposta com valores exra
    extra_values = db.get_extra_values(response_values, auth_values)

    if has_domain and len(response_values) > 0:
        # Response code 0: Nenhum erro, o sistema tem informação direta sobre a query
        response_packet = recv_packet.response("A",0,response_values,auth_values,extra_values)
        # Guardar em Cache
        pass
    elif has_domain:
        # Response code 1: O dominio existe mas não encontrou informação com o TYPE_OF_VALUE necessário
        # Resultados vazio e auth e extra normais.
        response_packet = recv_packet.response("A",1,response_values,auth_values,extra_values)
        # Resposta Negativa e pode ser guardada em cache durante um "horizonte temporal curto"
        pass
    elif not has_domain:
        # Response code 2: O dominio não existe mas inclui os auth de onde obteu informação
        response_packet = recv_packet.response("A",2,response_values,auth_values,extra_values)
        # Resposta Negativa e pode ser guardada em cache
        pass
    else:
        #Response code 3: Mensagem DNS não descodificada corretamente
        response_packet = recv_packet.response("A",3,response_values,auth_values,extra_values)
        # Log Erro na descodificacao
        time = datetime.datetime.now()
        log.logEntry(time, "ER", ipLog(address[0], address[1]), "Especificar o Erro, e onde ocorreu")

    msg = response_packet.str()
    UDPServerSocket.sendto(msg.encode(), address)

    # Log Resposta à query enviada
    time = datetime.datetime.now()
    log.logEntry(time, "RE", ipLog(address[0], address[1]), msg)

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

        thread = Thread(target=query_handler,args=(address,message,UDPServerSocket,db, log))
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
        thread = Thread(target=zone_transfer_handler,args=(connection,address,db,configs,log))
        thread.start()

if __name__ == '__main__':
    args = sys.argv[1:]

    print("------------SP----------------")

    # Leitura do ficheiro de configuração
    configs = Configuration()
    configs.parse_from_file(args[0])

    # Inicializa o Log
    log = Log(configs.lg[0]['filepath'], "shy")

    if len(configs.db) > 1:
        # fazer uma lista de dicionarios dominio-db_correspondente
        # este é o caso em que é um sp de um dominio de topo ou seja tem mais que uma base de dados
        pass
    else:
        db = Database()
        db.parse_from_file(configs.db[0]['filepath'])
        # Log Database Read
        time = datetime.datetime.now()
        log.logEntry(time, "EV", "127.0.0.1", evLogData("db-file-read", configs.db[0]['filepath']))

    # Leitura do ficheiro com a lista dos servidores de topo
    sdts = SdtServers()
    sdts.parse_from_file(configs.st['filepath'])
    # Log ST Read
    time = datetime.datetime.now()
    log.logEntry(time, "EV", "127.0.0.1", evLogData("st-file-read", configs.st['filepath']))

    # Inicialização dos serviços de Query e ZoneTransfer
    thread1 = Thread(target=zone_transfer_sevice)
    thread2 = Thread(target=query_service)
    thread1.start()
    thread2.start()
