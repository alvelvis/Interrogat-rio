#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import os
import cgi, cgitb
cgitb.enable()
import interrogar_UD
from functions import prettyDate, fromInterrogarToHtml
from datetime import datetime

form = cgi.FieldStorage()
corpus = form['corpus'].value
pesquisa = form['params'].value
criterio = pesquisa.split(' ')[0]
parametros = pesquisa.split(' ', 1)[1]

ocorrencias = interrogar_UD.main('../interrogar-ud/conllu/' + corpus, int(criterio), parametros)['output']
numeroOcorrencias = len(ocorrencias)

html = f"<title>Exportar resultados para .html - Interrogatório</title><h1>Exportar resultados para .html</h1><a href='javascript:window.close()'>Fechar</a><hr>Página gerada dia {prettyDate(datetime.now()).beautifyDateDMAH()}<br>Corpus: <a href='../interrogar-ud/conllu/{corpus}' download>{corpus}</a><br>Busca: <a target='_blank' href='../cgi-bin/interrogar.cgi?corpus={corpus}&params={pesquisa}'>{pesquisa}</a><br>Resultados: {numeroOcorrencias}<hr><br>"
html += "\n".join([str(i+1) + '/' + str(numeroOcorrencias) + ' - ' + fromInterrogarToHtml(x['resultadoAnotado'].sent_id) + ': ' + fromInterrogarToHtml(x['resultadoAnotado'].text) + '<hr>' for i, x in enumerate(ocorrencias)])
print(html)