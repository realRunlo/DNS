import socket
import time
import sys
import json
import re
from parsers import *
from threading import Thread
from DnsPacket import *
from logsys import *

# shy | debug
logMode = "shy"

def zone_transfer_handler(db,domain,sp_ip, log):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((sp_ip, 6000))

    request_db_serial_msg = "getserial:"
    # Envia pedido para saber número de série da db do SP
    s.sendall(request_db_serial_msg.encode('utf-8'))
    timeStart = datetime.datetime.now()

    # Recebe número de série da db do SP
    db_serial = s.recv(1024)

    total_entries = 0
    # Se a versão for diferente da que está no SP ou o SS ainda não tiver a base de dados carregada
    if db.soaserial=={} or db_serial.decode('utf-8') != db.soaserial['value']:
        #  SS envia  o nome completo do domínio para a qual quer receber uma cópia da base de dados do SP
        send_domain = "domain:"+domain
        s.sendall(send_domain.encode('utf-8'))

        sp_response = s.recv(1024).decode('utf-8').split(":")
        sp_response_type = sp_response[0]
        sp_response_msg = sp_response[1]

        # Quando ss tem permissão
        if sp_response_type == "entries":
            total_entries = int(sp_response_msg)

            if total_entries<=65535:
                # SS aceita o número de entradas
                s.sendall("ok:".encode('utf-8'))

                last_entry = 0
                while total_entries>0:
                    entrie_msg = s.recv(200)
                    entrie_msg = entrie_msg.decode('utf-8')

                    fields = entrie_msg.split(";")

                    entry_number = int(fields[0])
                    entry = json.loads(fields[1])

                    # Adciona entrada à base de dados
                    db.add_entry(entry['type'],entry)
                    total_entries -= 1

                    # Regista Log
                    timeEnd = datetime.datetime.now()
                    log.logEntry(timeEnd, "ZT", ipLog(sp_ip, 6000), ztLogData("SS", timeStart, timeEnd))

                    # SS já tem a base de dados em memória, abandona coneção
                    s.close()
                    print("Transferência de zona terminada")
                    db.print()

        # Quando ss não tem permissão
        elif sp_response_type == "error":
            print(sp_response_msg)

    else:
        #Não precisa de atualiza a bd
        s.sendall("abandon:".encode('utf-8'))
        s.close()

def query_handler(my_address,address,message,UDPServerSocket,db, log):
    msg = ""
    bufferSize =1024
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

    if domain == "" and db.has_domain("."):
        domain = "."

    # Verifica se existe dominio
    has_domain = db.has_domain(domain)
    # Resposta com aquele nome de dominio e tipo na base de dados
    response_values = db.get_response_values(recv_packet.name,recv_packet.value_type)
    # Resposta com servidores autoritativos
    auth_values = db.get_auth_values(domain)
    # Resposta com valores exra
    extra_values = db.get_extra_values(response_values, auth_values)

    if len(extra_values) > 0:
        new_ip = extra_values[0]['value']
        flag = True
    else:
        flag = False

    # Final Response not obtained in this server
    if 'R' in recv_packet.flags and flag and len(extra_values) < 2:
        # Create secondary socket
        SecondServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        SecondServerSocket.bind((my_address, 5554))

        # Send to next server
        SecondServerSocket.sendto(message, (new_ip, 5555))

        # Receive from server
        bytesAddressPair = SecondServerSocket.recvfrom(bufferSize)

        # Send response to client
        msg = bytesAddressPair[0].decode()
        UDPServerSocket.sendto(bytesAddressPair[0], address)

    else:
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
    time.sleep(5)
    bufferSize = 1024
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    my_address = db.a[1]["value"]
    print(my_address)

    # Bind to address and ip
    UDPServerSocket.bind((my_address, 5555))

    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        thread = Thread(target=query_handler,args=(my_address, address,message,UDPServerSocket,db, log))
        thread.start()

def zone_transfer_sevice():

    while True:
        thread3 = Thread(target=zone_transfer_handler,args=(db,configs.sp[0]["dominio"],configs.sp[0]["ip_port"], log))
        thread3.start()
        thread3.join()

        time.sleep(int(db.soarefresh["value"]))


if __name__ == '__main__':
    args = sys.argv[1:]

    print("------------SS----------------")

    # Leitura do ficheiro de configuração
    configs = Configuration()
    configs.parse_from_file(args[0])

    # Inicializa o Log
    log = Log(configs.lg[0]['filepath'], logMode)

    # Leitura do ficheiro com a lista dos servidores de topo
    #sdts = SdtServers()
    #sdts.parse_from_file(configs.st['filepath'])

    db = Database()

    thread1 = Thread(target=zone_transfer_sevice)
    thread2 = Thread(target=query_service)
    thread1.start()
    thread2.start()
