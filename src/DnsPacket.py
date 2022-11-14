


class DnsPAcket:

    def __init__(self):
		pass


    def encode(self,message_id,flags,response_code,n_values,n_auth,n_extras,query_info,response_val,auth_vals,extra_vals):
        # Codificar um DNS packet
        pass


    # mensagem em formato string (sem codificação binária) para teste
    def str(self,message_id,flags,response_code,n_values,n_auth,n_extras,query_info,response_val,auth_vals,extra_vals):

        return message_id+";"flags+";"+response_code+";"+n_values+";"+n_auth+";"+n_extras+";"+query_info+";"+response_val+";"+auth_vals+";"+extra_vals
