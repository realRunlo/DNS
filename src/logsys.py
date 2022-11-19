import datetime


class Log():

    def __init__(self,filename,mode):
        self.filename = filename
        self.mode = mode
        pass

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
