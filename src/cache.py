import threading
import datetime

class Block():

    def __init__(self,entry):
        # Marca o tempo em que foi dada a entrada na cache
        self.timestamp = datetime.datetime.now()
        self.entry = entry

class Cache():

    def __init__(self):
        self.lock = threading.Lock()
        self.ns = []
        self.a = []
        self.mx = []
        pass

    def write(self,entry):
        new_block = Block(entry)
        if entry['type'] == "NS":
            self.ns.append(new_block)
        elif entry['type'] == "A":
            self.a.append(new_block)
        elif  entry['type'] == "MX":
            self.mx.append(new_block)

    def cache_packet(self,packet):
        self.lock.acquire()
        try:
            values = []
            response_vals = self.response_vals.split(",")
            auth_vals = self.auth_vals.split(",")
            extra_vals = slef.extra_vals.split(",")

            values.append(response_vals)
            values.append(auth_vals)
            values.append(extra_vals)

            # Regista os valores enviados no packet em cache
            for value in values:
                fields = value.split(" ")
                n_fields = len(flieds)
                if n_fields==3:
                    entry = { "parameter" : fields[0] , "type" : fields[1] , "value" : fields[2] }
                elif n_fields==4:
                    entry = { "parameter" : fields[0] , "type" : fields[1] , "value" : fields[2] , "ttl" : fields[3]  }
                elif n_fields==5:
                    entry = { "parameter" : fields[0] , "type" : fields[1] , "value" : fields[2] , "ttl" : fields[3] , "prio" : fields[4]  }
                self.write(entry)

        finally:
            self.lock.release()


    def get_response_values(self,name,value_type):
        self.lock.acquire()
        try:
            now = datetime.datetime.now()
            res = []
            type = value_type.lower()
            for block in getattr(self,type):
                if(block.entry.['parameter']==name):
                    if "ttl" in block.entry:
                        if now - block.timestamp < float(block.entry.['ttl']):
                            res.append(block.entry)

                    else:# Se não tiver ttl definido é adicionado tbm
                        res.append(block.entry)
            return res
        finally:
            self.lock.release()

    def get_auth_values(self,name):
        self.lock.acquire()

        try:
            now = datetime.datetime.now()
            res = []
            for block in self.ns:
                if(block.entry.['parameter']==name):
                    if "ttl" in block.entry:
                        if now - block.timestamp < float(block.entry.['ttl']):
                            res.append(block.entry)
                    else:
                        res.append(block.entry)

            return res
        finally:
            self.lock.release()

    def get_extra_values(self,response,values):
        self.lock.acquire()
        try:
            now = datetime.datetime.now()
            extra = []
            for each in response:
                for block in self.a:
                    # NOTE: Queries do tipo A têm "each" do tipo diferente das queries do tipo MX
                    # value para MX e parameter para A
                    if (each['value']==block.entry['parameter'] or each['parameter']==block.entry['parameter']):
                        if "ttl" in block.entry:
                            if now - block.timestamp < float(block.entry.['ttl']):
                                extra.append(elem)
                        else:
                            extra.append(elem)
                        break

            for each in auth:
                for block in self.a:
                    if (each['value']==block.entry['parameter']):
                        if "ttl" in block.entry:
                            if now - block.timestamp < float(block.entry.['ttl']):
                                extra.append(block.entry)
                        else:
                            extra.append(block.entry)
                        break
            return extra

        finally:
            self.lock.release()
