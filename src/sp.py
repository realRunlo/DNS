import socket
from threading import Thread
import sys
from parsers import *

def query_handler(adress,massage):
    pass


if __name__ == '__main__':

    args = sys.argv[1:]

    # Leitura do ficheiro de configuração
    configs = Configuration.parse_from_file(args[0])
    # Leitura do ficheiro com a lista dos servidores de topo
    sdts = SdtServers.parse_from_file(args[1])
    #Leitura com ficheiro de base de dados
    db = Database().parse_from_file(args[2])

    bufferSize = 1024
    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    UDPServerSocket.bind(("127.0.0.1", 5555))


    while(True):

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        thread = Thread(target=query_handler,args=(address,message))
        thread.start()
