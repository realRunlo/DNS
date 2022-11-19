import re

# Classe dos dados de configuração
class Configuration:

    def __init__(self):
        self.db = []
        self.sp = []
        self.ss = []

    def parse_from_file(self,filename):
        fp = open(filename,"r")
        exp = re.compile(r'(?P<parametro>[\w.]+)\s(?P<tipo>DB||SP||SS||DD||ST||LG)\s(?P<associado>[\w.\/\-:]+)')

        for line in fp:
            res = exp.match(line)
            if res:
                if res.group("tipo")=="DB":
                    self.db.append({"dominio" : res.group("parametro"), "filepath" : res.group("associado")})
                elif res.group("tipo")=="SP":
                    self.sp.append({"dominio" : res.group("parametro"), "ip_port" : res.group("associado")})
                elif res.group("tipo")=="SS":
                    self.ss.append({"dominio" : res.group("parametro"), "ip_port" : res.group("associado")})
                elif res.group("tipo")=="DD":
                    pass
                elif res.group("tipo")=="ST":
                    self.st = {"filepath" : res.group("associado")}
                elif res.group("tipo")=="LG":
                    self.lg = {"filepath" : res.group("associado")}
                else:
                    # Fazer report de incoerências ou erros
                    pass
        return self



# Classe com a lista de servidores de topo
class SdtServers():
    def __init__(self):
        self.table = []

    def parse_from_file(self,filename):
        fp = open(filename,"r")
        exp = re.compile(r'^(?P<ip>(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])):(?P<port>[0-9]+)$')

        for line in fp:
            res = exp.match(line)
            if res:
                self.table.append((res.group("ip"),res.group("port")))
            else:
                # Fazer report de incoerências ou erros
                pass


        return self


# Classe da base de dados de um servidor primário
class Database:

    def __init__(self):
        self.soasp = {}
        self.soaadmin = {}
        self.soaserial = {}
        self.soarefresh = {}
        self.soaretry = {}
        self.soaexpire = {}

        self.ns = []
        self.a = []
        self.mx = []


    def parse_from_file(self,filename):
        fp = open(filename,"r")
        # Expressão que dá match com as entradas do tipo DEFAULT
        exp_default = re.compile(r'(?P<macro>[^\s]+)\sDEFAULT\s(?P<valor>[^\s]+)')
        # Expressão que dá match com as entradas do tipo CNAME
        exp_cname = re.compile(r'(?P<alias>[^\s]+)\sCNAME\s(?P<valor>[^\s]+)\s(?P<tempo>[^\s]+)')
        # Expressão que dá match com as entradas do tipo SOASP||SOAADMIN||SOASERIAL||SOAREFRESH||SOARETRY||SOAEXPIRE
        exp_soa = re.compile(r'(?P<parametro>[^\s]+)\s(?P<tipo>SOASP||SOAADMIN||SOASERIAL||SOAREFRESH||SOARETRY||SOAEXPIRE)\s(?P<valor>[^\s]+)\s(?P<tempo>[^\s]+)')


        exp_priority = re.compile(r'(?P<parametro>[^\s]+)\s(?P<tipo>NS||A||CNAME||MX)\s(?P<valor>[^\s]+)\s(?P<tempo>[^\s]+)\s(?P<prioridade>[^\s]+)$')

        exp_ttl = re.compile(r'(?P<parametro>[^\s]+)\s(?P<tipo>NS||A||CNAME||MX)\s(?P<valor>[^\s]+)\s(?P<tempo>[^\s]+)$')

        exp_value = re.compile(r'(?P<parametro>[^\s]+)\s(?P<tipo>NS||A||CNAME||MX)\s(?P<valor>[^\s]+)$')


        macros = []
        alias = []
        for line in fp:
            # Dá macth aos alias de definidos
            res_default = exp_default.match(line)
            if res_default:
                macros.append([res_default.group("macro"),res_default.group("valor")])
            else:
                # Percorre os alias estabelecidos e faz a substituição, parte-se do princípio
                # que os alias são definidos no inicio de ficheiro
                for macro in macros:
                    line = re.sub(macro[0],macro[1],line)

                res_soa = exp_soa.match(line)
                res_priority = exp_priority.match(line)
                res_ttl = exp_ttl.match(line)
                res_value = exp_value.match(line)
                if res_soa:
                    if res_soa.group("tipo") == "SOASP":
                        # Valor indica o nome completo do SP do domínio (ou zona) indicado no parâmetro
                        self.soasp = {"parameter": res_soa.group("parametro"),"value" : res_soa.group("valor"),"ttl" : res_soa.group("tempo")}
                    elif res_soa.group("tipo") == "SOAADMIN":

                        # Valor indica o endereço de e-mail completo do administrador do domínio (ou zona) indicado n parâmetro
                        self.soaadmin = {"parameter": res_soa.group("parametro"),"value" : re.sub("\\\.","@",res_soa.group("valor")),"ttl" : res_soa.group("tempo")}
                    elif res_soa.group("tipo") == "SOASERIAL":
                        # Valor indica o número de série da base de dados do SP do domínio (ou zona)indicado no parâmetro
                        self.soaserial = {"parameter": res_soa.group("parametro"),"value" : res_soa.group("valor"),"ttl" : res_soa.group("tempo")}
                    elif res_soa.group("tipo") == "SOAREFRESH":
                        # Valor indica o intervalo temporal em segundos para um SS perguntar ao SP do domínio indicado no parâmetro qual o número de série da base de dados dessa zona;
                        self.soarefresh = {"parameter": res_soa.group("parametro"),"value" : res_soa.group("valor"),"ttl" : res_soa.group("tempo")}
                    elif res_soa.group("tipo") == "SOARETRY":
                        #o valor indica o intervalo temporal para um SS voltar a perguntar ao SP do domínio indicado no parâmetro qual o número de série da base de dados dessa zona, após um timeout
                        self.soaretry = {"parameter": res_soa.group("parametro"),"value" : res_soa.group("valor"),"ttl" : res_soa.group("tempo")}
                    elif res_soa.group("tipo") == "SOAEXPIRE":
                        # Valor indica o intervalo temporal para um SS deixar de considerar a sua réplica da base de dados da zona indicada no parâmetro como válida
                        self.soaexpire = {"parameter": res_soa.group("parametro"),"value" : res_soa.group("valor"),"ttl" : res_soa.group("tempo")}
                elif res_priority:
                    entry = {"parameter": res_priority.group("parametro"),"value" : res_priority.group("valor"),"ttl" : res_priority.group("tempo"),"prio" :res_priority.group("prioridade") }
                    if res_priority.group("tipo") == "NS":
                        self.ns.append(entry)
                    elif res_priority.group("tipo") == "A":
                        self.a.append(entry)
                    elif res_priority.group("tipo") == "MX":
                        self.mx.append(entry)
                    else:
                        # Fazer report de incoerências ou erros
                        pass

                elif res_ttl:
                    entry = {"parameter": res_ttl.group("parametro"),"value" : res_ttl.group("valor"),"ttl" : res_ttl.group("tempo")}
                    if res_ttl.group("tipo") == "NS":
                        self.ns.append(entry)
                    elif res_ttl.group("tipo") == "A":
                        self.a.append(entry)
                    elif res_ttl.group("tipo") == "MX":
                        self.mx.append(entry)
                    else:
                        # Fazer report de incoerências ou erros
                        pass
                elif res_value:
                    entry = {"parameter": res_value.group("parametro"),"value" : res_value.group("valor")}
                    if res_value.group("tipo") == "NS":
                        self.ns.append(entry)
                    elif res_value.group("tipo") == "A":
                        self.a.append(entry)
                    elif res_value.group("tipo") == "MX":
                        self.mx.append(entry)
                    else:
                        # Fazer report de incoerências ou erros
                        pass
        return self



    def size(self):
        total_entries = 0
        total_entries += len(self.ns) + len(self.a) + len(self.mx) + 6

        return total_entries

    def add_entry(self,type,entry):
        if type=="soasp":
            self.soasp = entry
        elif type=="soaadmin":
            self.soaadmin = entry
        elif type=="soaserial":
            self.soaserial = entry
        elif type=="soarefresh":
            self.soarefresh = entry
        elif type=="soaretry":
            self.soaretry = entry
        elif type=="soaexpire":
            self.soaexpire = entry
        elif type=="ns":
            self.ns.append(entry)
        elif type=="a":
            self.a.append(entry)
        elif type=="mx":
            self.mx.append(entry)

    # Metodo para criar lista com as entradas da db, o tipo tem quer adicionado a cada entrada
    def to_list(self):
        list = []

        elem = self.soasp
        elem["type"] = "soasp"
        list.append(elem)
        elem = self.soaadmin
        elem["type"] = "soaadmin"
        list.append(self.soaadmin)
        elem = self.soaserial
        elem["type"] = "soaserial"
        list.append(self.soaserial)
        elem = self.soarefresh
        elem["type"] = "soarefresh"
        list.append(self.soarefresh)
        elem = self.soaretry
        elem["type"] = "soaretry"
        list.append(self.soaretry)
        elem = self.soaexpire
        elem["type"] = "soaexpire"
        list.append(self.soaexpire)


        for elem in self.ns:
            elem["type"] = "ns"
            list.append(elem)
        for elem in self.mx:
            elem["type"] = "mx"
            list.append(elem)
        for elem in self.a:
            elem["type"] = "a"
            list.append(elem)

        return list




    def print(self):
        print("SOASP: " + str(self.soasp))
        print("SOAADMIN: " + str(self.soaadmin))
        print("SOASERIAL: " + str(self.soaserial))
        print("SOAREFRESH: " + str(self.soarefresh))
        print("SOARETRY: " + str(self.soaretry))
        print("SOAEXPIRE: " + str(self.soaexpire))

        print("NS")
        for elem in self.ns:
            print(elem)

        print("MX")
        for elem in self.mx:
            print(elem)

        print("A")
        for elem in self.a:
            print(elem)

    # Lista das entradas que fazem match no NAME e TYPE OF VALUE na base de dados do servidor autoritativo
    def get_response_values(self,name,value_type):
        res = []
        type = value_type.lower()
        for elem in getattr(self,type):
            if(elem['parameter']==name):
                elem['type'] = value_type
                res.append(elem)
        return res

    # Lista das entradas que fazem match com o NAME e com o tipo de valor igual
    # a NS na base de dados do servidor autoritativo
    def get_auth_values(self,name):
        res = []
        for elem in self.ns:
            if(elem['parameter']==name):
                elem['type'] = "NS"
                res.append(elem)
        return res

    # Lista das entradas do tipo A (incluídos na cache ou na base de dados do servidor autoritativo) e que fazem
    # match no parâmetro com todos os valores no campo RESPONSE VALUES e no campo AUTHORITIES VALUES
    def get_extra_values(self,response_values,extra_values):
        res = []
        for elem in self.a:
            for rv in response_values:
                # Compara o parametro com a primeira parte do endereço no value
                if elem['parameter']==rv['value'].split(".")[0]:
                    elem['type'] = "A"
                    res.append(elem)

            for ev in extra_values:
                # Compara o parametro com a primeira parte do endereço no value
                if elem['parameter']==ev['value'].split(".")[0]:
                    elem['type'] = "A"
                    res.append(elem)
        return res
