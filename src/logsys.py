import datetime
import threading
import os
from DnsPacket import *

class Log():

    def __init__(self,filename,mode):
        self.filename = filename
        self.lock = threading.Lock()
        self.mode = mode

# Implementar  com locks... controlo de concorência
# Implementar todos os tipo de logging especificados

    def st(self,port,timeout):
        FILE = open(self.filename,"a+")
        now = datetime.datetime.now()
        log_str = now.strftime("%d:%m:%Y.%H:%M:%S") + " ST 127.0.0.1 " + port + " " + timeout + " " + self.mode

        FILE.write(log_str)
        FILE.close()

        if self.mode=="debug":
            print(log_str)


    def logEntry(self, time, type, ip, data):
        entry = time.strftime("%d:%m:%Y.%H:%M:%S ") + type + " " + ip + " " + data
        FILE = None
        if self.mode == "debug":
            print(entry)
        else:
            self.lock.acquire()
            try:
                FILE = open(self.filename,"a+")
                FILE.write(entry)
                FILE.close()
            finally:
                self.lock.release()

def ipLog(ip, port):
    return ip + ":" + str(port)

def ztLogData(serverType, timeStart, timeEnd):
    return serverType + " " + str((timeEnd-timeStart).total_seconds())

def evLogData(description, info):
    return description + " " + info
