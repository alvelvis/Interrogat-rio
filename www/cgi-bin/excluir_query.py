#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import os
import cgi,cgitb
cgitb.enable()
import re
import estrutura_dados
import estrutura_ud
import interrogar_UD
from datetime import datetime
import functions
from functions import tabela, prettyDate
import json
from credenciar import LOGIN
from functions import fromInterrogarToHtml

from estrutura_dados import slugify as slugify

form = cgi.FieldStorage()

if LOGIN:
    if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
        html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
        print(html)
        exit()

html = form['html'].value
json_id = form['json_id'].value

query_records_path = "./cgi-bin/json/query_records.json"
with open(query_records_path) as f:
    query_records = json.loads(f.read())
query_records[json_id]['persistent'] = False

if os.path.isfile("./cgi-bin/json/filtros.json"):
    with open("./cgi-bin/json/filtros.json") as f:
        filtros = json.load(f)
    if html in filtros:
        for filter_name in filtros[html]['filtros']:
            for parameter in filtros[html]['filtros'][filter_name]['parametros']:
                filter_json_id = parameter['json_id']
                query_records[filter_json_id]['persistent'] = False
        filtros.pop(html)
        with open("./cgi-bin/json/filtros.json", "w") as f:
            json.dump(filtros, f)
with open("./interrogar-ud/queries.txt") as f:
    queries = f.read()
queries = [x for x in queries.splitlines() if not html in x]
with open("./interrogar-ud/queries.txt", "w") as f:
    f.write("\n".join(queries))
with open(query_records_path, "w") as f:
    f.write(json.dumps(query_records))
os.remove(f"./interrogar-ud/resultados/{html}.html")

print("<script>window.location = '../cgi-bin/interrogatorio.py'</script>")
