#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

fastSearch = ['teste', 'Busca rápida']

import os
import sys
import cgi, cgitb
cgitb.enable()
import interrogar_UD
from functions import prettyDate, fromInterrogarToHtml
from datetime import datetime
import json

form = cgi.FieldStorage()
corpus = form['corpus'].value
pesquisa = form['params'].value
criterio = pesquisa.split(' ')[0]
parametros = pesquisa.split(' ', 1)[1]
nome = form['nome'].value
link = form['html'].value.rsplit("/", 1)[1].rsplit(".", 1)[0]
sys.stderr.write(link)

if os.path.isfile("../cgi-bin/filtros.json"):
    with open("../cgi-bin/filtros.json") as f:
        filtros = json.load(f)
else:
    filtros = []

ocorrencias = interrogar_UD.main('../interrogar-ud/conllu/' + corpus, int(criterio), parametros)['output']
numeroOcorrencias_antes = len(ocorrencias)
if nome not in fastSearch:
    ocorrencias = [x for x in ocorrencias if link not in filtros or x['resultadoEstruturado'].sent_id not in [x for filtro in filtros[link]['filtros'] for x in filtros[link]['filtros'][filtro]['sentences']]]
numeroOcorrencias = len(ocorrencias)

html = f"<script src=\"../../interrogar-ud/jquery-latest.js\"></script><script src=\"../../interrogar-ud/resultados.js?version=15\"></script><title>Exportar resultados para .html: Interrogatório</title><h1 class='translateHtml'>Exportar resultados para .html</h1><a class='translateHtml' href='javascript:window.close()'>Fechar</a><hr><span class='translateHtml'>Página gerada dia</span> {prettyDate(datetime.now()).beautifyDateDMAH()}<br><span class='translateHtml'>Corpus:</span> <a href='../interrogar-ud/conllu/{corpus}' download>{corpus}</a><br><span class='translateHtml'>Busca:</span> <a target='_blank' href='../cgi-bin/interrogar.cgi?corpus={corpus}&params={pesquisa}'>{pesquisa}</a><br><span class='translateHtml'>Resultados:</span> {numeroOcorrencias_antes}"
if nome not in fastSearch:
    if filtros and link in filtros:
        html += f"<br>Filtros: {len([x for filtro in filtros[link]['filtros'] for x in filtros[link]['filtros'][filtro]['sentences']])}"
    html += f"<br><span class='translateHtml'>Busca salva em</span> <a href='../interrogar-ud/resultados/{link}.html'>{nome}</a>"
html += "<hr><br>"
html += "\n".join(['<b>' + str(i+1) + '/' + str(numeroOcorrencias) + ' - ' + fromInterrogarToHtml(x['resultadoAnotado'].sent_id) + '</b><br>' + fromInterrogarToHtml(x['resultadoAnotado'].metadados['clean_text'] if 'clean_text' in x['resultadoAnotado'].metadados else x['resultadoAnotado'].text) + '<hr>' for i, x in enumerate(ocorrencias)])
print(html)