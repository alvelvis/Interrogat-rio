#!/usr/bin/env python3
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
if os.path.isfile(f"../interrogar-ud/resultados/{html}.html"):
    os.remove(f"../interrogar-ud/resultados/{html}.html")
else:
    print(f"{html} não encontrado")
if os.path.isfile("../cgi-bin/filtros.json"):
    with open("../cgi-bin/filtros.json") as f:
        filtros = json.load(f)
    if html in filtros:
        filtros.pop(html)
        with open("../cgi-bin/filtros.json", "w") as f:
            json.dump(filtros, f)
with open("../interrogar-ud/queries.txt") as f:
    queries = f.read()
queries = [x for x in queries.splitlines() if not html in x]
with open("../interrogar-ud/queries.txt", "w") as f:
    f.write("\n".join(queries))

print("<script>window.location = '../cgi-bin/interrogatorio.py'</script>")
