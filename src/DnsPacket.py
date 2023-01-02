

# # Formato binário
# class DnsPacket:
#
#     def __init__(self):
# 		pass
#
#
#     def encode(self,message_id,flags,response_code,n_response,n_auth,n_extra,query_info,response_val,auth_vals,extra_vals):
#         # Codificar um DNS packet
#         pass

# Formato conciso
class DnsConcisoPacket:

    def __init__(self):
        # Header fileds
        self.message_id = 0
        self.flags = ""
        self.response_code = 0
        self.n_response = 0
        self.n_auth = 0
        self.n_extra = 0
        # Query info fields
        self.name = ""
        self.value_type = ""
        # Data flieds
        self.response_vals = ""
        self.auth_vals = ""
        self.extra_vals =""

    def str(self):
        string = str(self.message_id)+","+self.flags+","+str(self.response_code)+","+str(self.n_response)+","+str(self.n_auth)+","+str(self.n_extra)+";"+self.name+","+self.value_type+";"+self.response_vals+";"+self.auth_vals+";"+self.extra_vals+";"
        flags = self.flags.split('+')
        for flag in flags:
            if flag=='Q': # If is query
                string = str(self.message_id)+","+self.flags+","+str(self.response_code)+","+str(self.n_response)+","+str(self.n_auth)+","+str(self.n_extra)+";"+self.name+","+self.value_type+";"

        return string

    def prettyStr(self):
        string = "# Header\n"
        string += "MESSAGE-ID = " + str(self.message_id) + ", FLAGS = " + self.flags + ", RESPONSE-CODE = " + str(self.response_code) + ",\n"
        string += "N-VALUES = " + str(self.n_response) + ", N-AUTHORITIES = " + str(self.n_auth) + ", N-EXTRA-VALUES = " + str(self.n_extra) + ";\n"
        string += "# Data: Query Info\n"
        string += "QUERY-INFO.NAME = " + self.name + ", QUERY-INFO.TYPE = " + self.value_type + ";\n"
        string += "# Data: List of Response, Authorities and Extra Values\n"
        for elem in self.response_vals.split(","):
            if elem=="":
                string += "RESPONSE-VALUES = (Null);\n"
            else:
                string += "RESPONSE-VALUES = " + elem + ",\n"
        string = string[:-2] + ";\n"
        for elem in self.auth_vals.split(","):
            if elem=="":
                string += "AUTHORITIES-VALUES = (Null);\n"
            else:
                string += "AUTHORITIES-VALUES = " + elem +",\n"
        string = string[:-2] + ";\n"
        for elem in self.extra_vals.split(","):
            if elem=="":
                string += "EXTRA-VALUES = (Null);\n"
            else:
                string += "EXTRA-VALUES = " + elem +",\n"
        string = string[:-2] + ";\n"

        return string

    def fromStr(self,string):
        fields = string.split(";")
        header_fileds = fields[0].split(",")
        query_fileds = fields[1].split(",")

        # Header fileds
        self.message_id = int(header_fileds[0])
        self.flags = header_fileds[1]
        self.response_code = int(header_fileds[2])
        self.n_response = int(header_fileds[3])
        self.n_auth = int(header_fileds[4])
        self.n_extra = int(header_fileds[5])
        # Query info fields
        self.name = query_fileds[0]
        self.value_type = query_fileds[1]

        is_query = False
        flags = header_fileds[1].split('+')
        for flag in flags:
            if 'Q' in flag: # If is query
                is_query = True

        if not is_query:
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
    def response(self,flags,response_code,response_values,auth_values,extra_values):
        self.flags = flags
        self.response_code = response_code
        self.n_response = len(response_values)
        self.n_auth = len(auth_values)
        self.n_extra = len(extra_values)

        for elem in response_values:
            n_fields = len(elem.keys())
            if n_fields==3:
                self.response_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+","
            elif n_fields==4:
                self.response_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+","
            elif n_fields==5:
                self.response_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+" "+elem['prio']+","
        self.response_vals = self.response_vals[:-1]
        for elem in auth_values:
            n_fields = len(elem.keys())
            if n_fields==3:
                self.auth_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+","
            elif n_fields==4:
                self.auth_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+","
            elif n_fields==5:
                self.auth_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+" "+elem['prio']+","
        self.auth_vals =  self.auth_vals[:-1]
        for elem in extra_values:
            n_fields = len(elem.keys())
            if n_fields==3:
                self.extra_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+","
            elif n_fields==4:
                self.extra_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+","
            elif n_fields==5:
                self.extra_vals += elem['parameter'] +" "+elem['type']+" "+elem['value']+" "+elem["ttl"]+" "+elem['prio']+","
        self.extra_vals = self.extra_vals[:-1]
        return self
