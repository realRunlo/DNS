import re

# Classe dos dados de configuração
class Configuration:
    def __init__(self):
        pass

    @classmethod
    def parse_from_file(self,filename):
        fp = open(filename,"r")
        exp = re.compile(r'(?P<parametro>[\w.]+)\s(?P<tipo>DB||SP||SS||DD||ST||LG)\s(?P<associado>[\w.\/\-:]+)')
        self.db = []
        self.sp = []
        self.ss = []
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



# Classe com a lista de servidores de topo
class SdtServers():
    def __init__(self):
        pass

    @classmethod
    def parse_from_file(self,filename):
        fp = open(filename,"r")
        exp = re.compile(r'^(?P<ip>(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])):(?P<port>[0-9]+)$')
        self.table = []
        for line in fp:
            res = exp.match(line)
            if res:
                self.table.append((res.group("ip"),res.group("port")))
            else:
                # Fazer report de incoerências ou erros
                pass


        print(self.table)


# Classe da base de dados de um servidor primário
class Database:
    def __init__(self):
        pass

    @classmethod
    def parse_from_file(self,filename):
        fp = open(filename,"r")
        # Expressão que dá match com as entradas do tipo DEFAULT
        exp_default = re.compile(r'(?P<macro>[^\s]+)\sDEFAULT\s(?P<valor>[^\s]+)')
        # Expressão que dá match com as entradas do tipo CNAME
        exp_cname = re.compile(r'(?P<alias>[^\s]+)\sCNAME\s(?P<valor>[^\s]+)\s(?P<tempo>[^\s]+)')
        # Expressão que dá match com as entradas do tipo SOASP||SOAADMIN||SOASERIAL||SOAREFRESH||SOARETRY||SOAEXPIRE
        exp_soa = re.compile('r(?P<parametro>[^\s]+)\s(?P<tipo>SOASP||SOAADMIN||SOASERIAL||SOAREFRESH||SOARETRY||SOAEXPIRE)\s(?P<valor>[^\s]+)\s(?P<tempo>[^\s]+)')


        exp_priority = re.compile(r'(?P<parametro>[^\s]+)\s(?P<tipo>NS||A||CNAME||MX)\s(?P<valor>[^\s]+)\s(?P<tempo>[^\s]+)\s(?P<prioridade>[^\s]+)$')

        exp_ttl = re.compile(r'(?P<parametro>[^\s]+)\s(?P<tipo>A||CNAME||MX)\s(?P<valor>[^\s]+)\s(?P<tempo>[^\s]+)$')

        exp_value = re.compile(r'(?P<parametro>[^\s]+)\s(?P<tipo>NS||A||CNAME||MX)\s(?P<valor>[^\s]+)$')

        self.ns = []
        self.a = []
        self.mx = []
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
                        self.soasp = {"name" : res_soa.group("valor"),"ttl" : res_soa.group("tempo")}
                    elif res_soa.group("tipo") == "SOAADMIN":
                        re.sub("\.","@",res_soa)
                        self.soaadmin = {"adress" : res_soa.group("valor"),"ttl" : res_soa.group("tempo")}
                    elif res_soa.group("tipo") == "SOASERIAL":
                        self.soaserial = {"serial" : res_soa.group("valor"),"ttl" : res_soa.group("tempo")}
                    elif res_soa.group("tipo") == "SOAREFRESH":
                        self.soarefresh = {"time" : res_soa.group("valor"),"ttl" : res_soa.group("tempo")}
                    elif res_soa.group("tipo") == "SOARETRY":
                        self.soaretry = {"time" : res_soa.group("valor"),"ttl" : res_soa.group("tempo")}
                    elif res_soa.group("tipo") == "SOAEXPIRE":
                        self.soaexpire = {"time" : res_soa.group("valor"),"ttl" : res_soa.group("tempo")}
                elif res_priority:
                    entry = {"name" : res_priority.group("valor"),"ttl" : res_priority.group("tempo"),"prio" :res_priority.group("prioridade") }
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
                    entry = {"name" : res_ttl.group("valor"),"ttl" : res_ttl.group("tempo")}
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
                    entry = {"name" : res_value.group("valor")}
                    if res_value.group("tipo") == "NS":
                        self.ns.append(entry)
                    elif res_value.group("tipo") == "A":
                        self.a.append(entry)
                    elif res_value.group("tipo") == "MX":
                        self.mx.append(entry)
                    else:
                        # Fazer report de incoerências ou erros
                        pass
