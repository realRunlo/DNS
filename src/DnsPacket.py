

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
        # Query info fields
        self.name = ""
        self.value_type = ""
        # Data flieds
        self.response_val = ""
        self.auth_vals = ""
        self.extra_vals =""

    def str(self):
        string = str(self.message_id)+","+self.flags+","+str(self.response_code)+","+str(self.n_values)+","+str(self.n_auth)+";"+self.name+","+self.value_type+";"+self.response_val+","+self.auth_vals+","+self.extra_vals
        return string

    def fromStr(self,string):
        fields = string.split(";")
        header_fileds = fields[0].split(",")
        query_fileds = fields[1].split(",")
        data_fileds = fields[2].split(",")
        # Header fileds
        self.message_id = int(header_fileds[0])
        self.flags = header_fileds[1]
        self.response_code = int(header_fileds[2])
        self.n_values = int(header_fileds[3])
        self.n_auth = int(header_fileds[4])
        # Query info fields
        self.name = query_fileds[0]
        self.value_type = query_fileds[1]
        # Data flieds
        self.response_val = data_fileds[0]
        self.auth_vals = data_fileds[1]
        self.extra_vals = data_fileds[2]


    # Query request
    def request(self,message_id,flags,name,value_type):
        self.message_id = message_id
        self.flags = flags
        self.name = name
        self.value_type = value_type

    # Query response
    def response(self):
        pass
