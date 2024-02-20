import re
import uuid
import html as web
import datetime
from estrutura_ud import col_to_idx
import json
import os

corpusGenericoInquerito = "bosque.conllu"
corpusGenericoExpressoes = "generico.conllu"
conllu_json_file = "./interrogar-ud/conllu.json"
udpipe = "udpipe-1.2.0"
modelo = "portuguese-bosque-ud-2.4-190531.udpipe"
localtime = 0
fastsearch = ["Busca rápida"]

tabela = {
    'yellow': 'green',
    'purple': 'purple',
    'blue': 'blue',
    'red': 'red',
    'cyan': 'cyan',
}

readable_date = lambda x: datetime.datetime.fromtimestamp(float(x)).strftime("%Y-%m-%d %H:%M")
query_is_python = lambda x: len(x.split('"')) > 2 or any(y in x for y in ["==", " = ", " != "]) or 'regex(' in x
query_is_tokens = lambda x: x.startswith("tokens=")
replace_regex = lambda x: x.replace('re.search( r"^(" + r', 'regex(').replace(' + r")$"', '').replace(".__dict__['", ".").replace("'] ", "")
view_dist_html = '''
<ul>
    <li><a style="cursor:pointer" class="verDist translateTitle" title="Número do token na sentença">id</a></li>
    <li><a style="cursor:pointer" class="verDist translateTitle" title="Forma da palavra">word</a></li>
    <li><a style="cursor:pointer" class="verDist translateTitle" title="Lema da palavra">lemma</a></li>
    <li><a style="cursor:pointer" class="verDist translateTitle" title="Classe gramatical">upos</a></li>
    <li><a style="cursor:pointer" class="verDist translateTitle" title="Classe gramatical específica">xpos</a></li>
    <li><a style="cursor:pointer" class="verDist translateTitle" title="Atributos morfológicos">feats</a></li>
    <li><a style="cursor:pointer" class="verDist translateTitle" title="Número do token do qual é dependente sintaticamente">dephead</a></li>
    <li><a style="cursor:pointer" class="verDist translateTitle" title="Relação de dependência">deprel</a></li>
    <li><a style="cursor:pointer" class="verDist translateTitle" title="Relação de dependência específica">deps</a></li>
    <li><a style="cursor:pointer" class="verDist translateTitle" title="Miscelânea">misc</a></li>
    <li><a style="cursor:pointer" class="verDist translateTitle translateHtml" title="Você pode digitar o nome de qualquer coluna">outro atributo</a></li>
    <li><a style="cursor:pointer" class="verDist translateTitle translateHtml" title="Dependentes sintáticos">dependentes</a></li>
</ul>
'''

def build_modifications_html(df, _id):
    output = ""
    rows = df[df._id == _id]
    date = rows.date.iloc[0]
    tag = rows.tag.iloc[0]
    conllu = rows.conllu.iloc[0]
    interrogatorio = rows.interrogatorio.iloc[0]
    query = rows['query'].iloc[0] if 'query' in rows.columns else None
    query_script_name = rows.query_script_name.iloc[0] if 'query_script_name' in rows.columns else None
    filters = rows.filters.iloc[0] if 'filters' in rows.columns else None

    output += f"<b>{readable_date(date)} ({len(rows)} tokens modificados)</b>"
    output += "<br>Nome da correção: %s" % tag
    if isinstance(query_script_name, str) and query_script_name:
        output += "<br>Script de busca: " + web.escape(query_script_name)
    output += "<br>Nome da busca: " + web.escape(interrogatorio)
    if isinstance(query, str) and query:
        output += "<br>Expressão de busca: %s" % query
    if isinstance(filters, str) and filters:
        output += "<br>Os seguintes filtros foram aplicados à busca: %s" % filters.replace("<sep>", ", ")

    output += "<br>Corpus: %s.conllu" % web.escape(conllu)
    output += "<hr>"
    output += "<pre>"
    len_df = len(rows.index)
    for i, idx in enumerate(rows.index):
        sent_id = str(rows["sent_id"][idx])
        text = rows["text"][idx]
        col = rows["col"][idx] if 'col' in rows.columns else None
        before = rows["before"][idx]
        after = rows["after"][idx]
        if col and (col in col_to_idx or col.startswith("col")):
            if col in col_to_idx:
                col_idx = col_to_idx[col]
            else:
                col_idx = int(col.split("col")[1])-1
            before = "\t".join([x if col_idx != i else "<b>%s</b>" % x for i, x in enumerate(before.split("\t"))])
            after = "\t".join([x if col_idx != i else "<b>%s</b>" % x for i, x in enumerate(after.split("\t"))])
        head = rows["head"][idx]
        if text:
            text = escape_html_except_bold(text) + "\n"
        if head:
            head = f"(head: {web.escape(str(head))})"
        output += f'{i+1}/{len_df} - {web.escape(sent_id)}\n{text}ANTES: {escape_html_except_bold(before)}\nDEPOIS: {escape_html_except_bold(after)} {head}\n\n'
    output += "</pre>"
    return output

def load_conllu_json():
    conllus = {}
    if os.path.isfile(conllu_json_file):
        with open(conllu_json_file) as f:
            conllus = json.load(f)
    return conllus

def delete_from_conllu_json(ud):
    conllus = load_conllu_json()
    if ud in conllus:
        del conllus[ud]
    save_conllu_json(conllus)

def save_conllu_json(conllus):
    with open(conllu_json_file, "w") as f:
        json.dump(conllus, f)

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
