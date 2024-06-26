#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print('Content-type:text/html; charset=utf-8')
print('\n\n')

import os
import sys
import cgi, cgitb
cgitb.enable()
import interrogar_UD
from utils import prettyDate, fromInterrogarToHtml, fastsearch
from datetime import datetime
import json

form = cgi.FieldStorage()
corpus = form['corpus'].value
pesquisa = form['params'].value
#criterio = pesquisa.split(' ')[0]
#parametros = pesquisa.split(' ', 1)[1]
parametros = pesquisa
nome = form['nome'].value
link = form['html'].value.rsplit("/", 1)[1].rsplit(".", 1)[0]
sys.stderr.write(link)

if os.path.isfile("./cgi-bin/json/filtros.json"):
    with open("./cgi-bin/json/filtros.json") as f:
        filtros = json.load(f)
else:
    filtros = []

ocorrencias = interrogar_UD.main('./interrogar-ud/conllu/' + corpus, "", parametros)['output']
numeroOcorrencias_antes = len(ocorrencias)
if nome not in fastsearch:
    ocorrencias = [x for x in ocorrencias if link not in filtros or x['resultadoEstruturado'].sent_id not in [x for filtro in filtros[link]['filtros'] for x in filtros[link]['filtros'][filtro]['sentences']]]
numeroOcorrencias = len(ocorrencias)

html = f"<title>Exportar resultados para .html: Interrogatório</title><h1 class='translateHtml'>Exportar resultados para .html</h1><!--a class='translateHtml' href='javascript:window.close()'>Fechar</a--><hr><span class='translateHtml'>Página gerada dia</span> {prettyDate(datetime.now()).beautifyDateDMAH()}<br><span class='translateHtml'>Corpus:</span> {corpus}<br><span class='translateHtml'>Busca:</span> {pesquisa}<br><span class='translateHtml'>Resultados</span>: {numeroOcorrencias_antes}"
if nome not in fastsearch:
    if filtros and link in filtros:
        html += f"<br><span class='translateHtml'>Filtros</span>: {len([x for filtro in filtros[link]['filtros'] for x in filtros[link]['filtros'][filtro]['sentences']])}"
    html += f"<br><span class='translateHtml'>Busca salva em</span> <a href='../interrogar-ud/resultados/{link}.html'>{nome}</a>"
html += "<hr>"
html += "\n".join(['<b>' + str(i+1) + '/' + str(numeroOcorrencias) + ' - ' + fromInterrogarToHtml(x['resultadoAnotado'].sent_id) + '</b><br>' + fromInterrogarToHtml(x['resultadoAnotado'].metadados['text_tokens'] if 'text_tokens' in x['resultadoAnotado'].metadados else x['resultadoAnotado'].text) + '<hr>' for i, x in enumerate(ocorrencias)])
html += "<br>"
print(html)