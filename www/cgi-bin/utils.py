import re
import uuid

corpusGenericoInquerito = "bosque.conllu"
corpusGenericoExpressoes = "generico.conllu"
udpipe = "udpipe-1.2.0"
modelo = "portuguese-bosque-ud-2.4-190531.udpipe"
localtime = 0
fastsearch = ["Busca rápida"]

col_to_idx = {
	'id': 0,
	'word': 1,
	'lemma': 2,
	'upos': 3,
	'xpos': 4,
	'feats': 5,
	'dephead': 6,
	'deprel': 7,
	'deps': 8,
	'misc': 9
}

idx_to_col = {v: k for k, v in col_to_idx.items()}

tabela = {	'yellow': 'green',
			'purple': 'purple',
			'blue': 'blue',
			'red': 'red',
			'cyan': 'cyan',
}

def save_query_json(query_json, persistent=False, name=""):
    '''JSON should be a interrogar_UD dictionary
    Returns json_id, which is the name of the json file (with transformed datetime)
    '''
    from datetime import datetime
    import os
    import json

    path = "./cgi-bin/json/"
    if not os.path.isdir(path):
        os.mkdir(path)

    # create query_records
    query_records_path = os.path.join(path, "query_records.json")
    if not os.path.isfile(query_records_path):
        with open(query_records_path, "w") as f:
            f.write("{}")

    # load query_records
    with open(query_records_path) as f:
        query_records = json.loads(f.read())

    # save query json
    now_datetime = datetime.now()
    json_id = str(uuid.uuid4())
    with open(os.path.join(path, json_id + ".json"), "w") as f:
        f.write(json.dumps(query_json))

    # save query_records
    query_records[json_id] = {'datetime': now_datetime.isoformat(), 'persistent': persistent, 'name': name}
    with open(query_records_path, "w") as f:
        f.write(json.dumps(query_records))

    return json_id

def slugify(value):
	return "".join(x if x.isalnum() or x == '.' or x == '-' else "_" for x in value)

def cleanEstruturaUD(s):
    return re.sub(r"<.*?>", "", re.sub(r"@.*?/", "", s))

def fromInterrogarToHtml(s):
    return s.replace('/BOLD', '</b>').replace('@BOLD', '<b>').replace('@YELLOW/', '<font color=' + tabela['yellow'] + '>').replace('@PURPLE/', '<font color=' + tabela['purple'] + '>').replace('@BLUE/', '<font color=' + tabela['blue'] + '>').replace('@RED/', '<font color=' + tabela['red'] + '>').replace('@CYAN/', '<font color=' + tabela['cyan'] + '>').replace('/FONT', '</font>')

def escape_html_except_bold(s):
    return s.replace("<b>", "@BOLD").replace("</b>", "/BOLD").replace("<", "&lt;").replace(">", "&gt;").replace("@BOLD", "<b>").replace("/BOLD", "</b>")

class prettyDate:

    def __init__(self, date):

        date = str(date)
        calendario_raw = "janeiro,fevereiro,março,abril,maio,junho,julho,agosto,setembro,outubro,novembro,dezembro"
        calendario = {i+1: mes for i, mes in enumerate(calendario_raw.split(","))}
        data = date.split(" ")[0].split("-")

        self.dia = int(data[2])
        self.mes = int(data[1])
        self.mesExtenso = calendario[self.mes]
        self.mesExtenso_3 = "".join(calendario[self.mes][:3])
        self.ano = int(data[0])		
        horabruta = date.split(" ")[1].rsplit(":", 1)[0]
        self.hora = int(horabruta.split(":")[0]) - localtime
        if self.hora < 0: self.hora = 24 + self.hora
        self.tempo = str(self.hora) + ":" + horabruta.split(":")[1]

    def beautifyDateDMAH(self):
        
        return f"{self.dia} de {self.mesExtenso_3}. {self.ano} {self.tempo}"

    def beautifyDateDMH(self):

        return f"{self.dia} de {self.mesExtenso_3}. às {self.tempo}"

    def beautifyDateDMA(self):

        return f"{self.dia} de {self.mesExtenso} de {self.ano}"

def encodeUrl(s):
    return s\
        .replace(' ', '%20')\
        .replace('#', '%23')\
        .replace('$', '%24')\
        .replace("&", "%26")\
        .replace("@", "%40")\
        .replace('`', "%60")\
        .replace('/', "%2F")\
        .replace(":", "%3A")\
        .replace(";", "%3B")\
        .replace("<", "%3C")\
        .replace("=", "%3D")\
        .replace(">", "%3E")\
        .replace("?", "%3F")\
        .replace("[", "%5B")\
        .replace("\\", "%5C")\
        .replace("]", "%5D")\
        .replace("^", "%5E")\
        .replace("{", "%7B")\
        .replace("|", "%7C")\
        .replace("}", "%7D")\
        .replace("~", "%7E")\
        .replace('"', "%22")\
        .replace("'", "%27")\
        .replace("+", "%2B")\
        .replace(",", "%2C")
