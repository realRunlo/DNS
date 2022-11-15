

# # Formato binário
# class DnsPacket:
#
#     def __init__(self):
# 		pass
#
#
#     def encode(self,message_id,flags,response_code,n_values,n_auth,n_extras,query_info,response_val,auth_vals,extra_vals):
#         # Codificar um DNS packet
#         pass

# Formato conciso
class DnsConcisoPacket:

    def __init__(self):
        # Header fileds
        self.message_id = 0
        self.flags = ""
        self.response_code = 0
        self.n_values = 0
        self.n_auth = 0
        self.n_extras = 0
        # Query info fields
        self.name = ""
        self.value_type = ""
        # Data flieds
        self.response_vals = ""
        self.auth_vals = ""
        self.extra_vals =""

    def str(self):
        string = str(self.message_id)+","+self.flags+","+str(self.response_code)+","+str(self.n_values)+","+str(self.n_auth)+","+str(self.n_extras)+";"+self.name+","+self.value_type+";"+self.response_vals+";"+self.auth_vals+";"+self.extra_vals+";"
        return string

    def fromStr(self,string):
        fields = string.split(";")
        header_fileds = fields[0].split(",")
        query_fileds = fields[1].split(",")
        # Header fileds
        self.message_id = int(header_fileds[0])
        self.flags = header_fileds[1]
        self.response_code = int(header_fileds[2])
        self.n_values = int(header_fileds[3])
        self.n_auth = int(header_fileds[4])
        self.n_extras = int(header_fileds[5])
        # Query info fields
        self.name = query_fileds[0]
        self.value_type = query_fileds[1]
        # Data flieds
        self.response_vals = fields[2]
        self.auth_vals = fields[3]
        self.extra_vals = fields[4]


    # Query request
    def request(self,message_id,flags,name,value_type):
        self.message_id = message_id
        self.flags = flags
        self.name = name
        self.value_type = value_type

        return self

    # Query response
    def response(self,flags,response_values,auth_values,extra_values):
        self.flags = flags
        self.n_values = len(response_values)
        self.n_auth = len(auth_values)
        self.extras = len(extra_values)

        for elem in response_values:
            n_fields = len(elem.keys())
            if n_fields==3:
                self.response_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+",\n"
            elif n_fields==4:
                self.response_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+",\n"
            elif n_fields==5:
                self.response_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+" "+elem['prio']+",\n"
        self.response_vals = "\n" + self.response_vals[:-2]
        for elem in auth_values:
            n_fields = len(elem.keys())
            if n_fields==3:
                self.auth_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+", \n"
            elif n_fields==4:
                self.auth_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+", \n"
            elif n_fields==5:
                self.auth_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+" "+elem['prio']+", \n"
        self.auth_vals =  "\n" + self.auth_vals[:-2]
        for elem in extra_values:
            n_fields = len(elem.keys())
            if n_fields==3:
                self.extra_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+",\n"
            elif n_fields==4:
                self.extra_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+",\n"
            elif n_fields==5:
                self.extra_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+" "+elem['prio']+", \n"
        self.extra_vals = "\n" + self.extra_vals[:-2]
        pass

        return self
