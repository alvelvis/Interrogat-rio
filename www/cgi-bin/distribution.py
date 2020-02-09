#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html")
print('\n\n')

fastSearch = ['teste', 'Busca rápida']

import os
import cgi,cgitb
cgitb.enable()
import re
from datetime import datetime
from functions import tabela, prettyDate, encodeUrl
import datetime
import html as web
import estrutura_ud
import interrogar_UD
import json

#if not 'REQUEST_METHOD' in os.environ:
#	os.environ['REQUEST_METHOD'] = 'POST'

from estrutura_dados import slugify as slugify

#POST
form = cgi.FieldStorage()

filtros = []
nome_interrogatorio = ""
if "link_dist" in form and os.path.isfile("../cgi-bin/filtros.json"):
	link_interrogatorio = form['link_dist'].value.rsplit(".", 1)[0].rsplit("/", 1)[1]
	nome_interrogatorio = form['combination'].value
	with open("../cgi-bin/filtros.json") as f:
		filtros = json.load(f)
	if link_interrogatorio in filtros:
		filtros = [x for filtro in filtros[link_interrogatorio]['filtros'] for x in filtros[link_interrogatorio]['filtros'][filtro]['sentences']]
	else:
		filtros = []

sentences = interrogar_UD.main("../interrogar-ud/conllu/" + form['corpus'].value, 5, form['notSaved'].value)['output']
corpus = list()
for sentence in sentences:
	sent = estrutura_ud.Sentence()
	sent.build(sentence['resultado'].replace(f"@YELLOW/", "").replace(f"@RED/", "").replace(f"@CYAN/", "").replace(f"@BLUE/", "").replace(f"@PURPLE/", "").replace("/FONT", ""))
	if sent.sent_id not in filtros:
		corpus.append(sent)

dist = list()
for sentence in corpus:
	for token in sentence.tokens:
		if '<b>' in token.to_str() or "</b>" in token.to_str():
			dist.append(token.col.get(form["coluna"].value))

dicionario = dict()
for entrada in dist:
	entrada = entrada.replace("<b>", "").replace("</b>", "")
	if not entrada in dicionario: dicionario[entrada] = 1
	else: dicionario[entrada] += 1

lista = list()
for entrada in dicionario:
	lista.append((entrada, dicionario[entrada]))

pagina = '''
	<button onclick="topFunction()" id="myBtn" title="Voltar ao topo">Voltar ao topo</button>
	<style>
		#myBtn {
			display: none; /* Hidden by default */
			position: fixed; /* Fixed/sticky position */
			bottom: 20px; /* Place the button at the bottom of the page */
			right: 30px; /* Place the button 30px from the right */
			z-index: 99; /* Make sure it does not overlap */
			border: none; /* Remove borders */
			outline: none; /* Remove outline */
			background-color: rgba(255,105,30,1); /* Set a background color */
			color: white; /* Text color */
			cursor: pointer; /* Add a mouse pointer on hover */
			padding: 10px 15px; /* Some padding */
			border-radius: 20px; /* Rounded corners */
			font-size: 16px; /* Increase font size */
		}

		#myBtn:hover {
			background-color: #555; /* Add a dark-grey background on hover */
		}
	</style>
	<script src="../interrogar-ud/jquery.min.js"></script>
	<script src="../interrogar-ud/resultados.js?version=12"></script>
'''
pagina += "<title>Distribuição de " + form["coluna"].value + "</title>"
pagina += "<h1>Distribuição de " + form["coluna"].value + "</h1>"
pagina += '<a href="#" onclick="window.close()">Fechar</a><br><br>Relatório gerado dia ' + prettyDate(str(datetime.datetime.now())).beautifyDateDMAH() + ''
pagina += f"<hr>Busca: <a target='_blank' href='../cgi-bin/interrogar.cgi?corpus={form['corpus'].value}&params={form['expressao'].value}'>" + form["expressao"].value + "</a><br>"
pagina += "Corpus: <a href='../interrogar-ud/conllu/"+form["corpus"].value+"' title='Baixar corpus' download>" + form["corpus"].value + "</a>"
pagina += "<br><br>Quantidade de ocorrências: "+str(len(dist))+"<br>Quantidade de <b>"+form["coluna"].value+"</b>: "+str(len(lista))
if nome_interrogatorio and nome_interrogatorio not in fastSearch:
	pagina += f"<br>Busca salva em <a href='../interrogar-ud/resultados/{link_interrogatorio}.html'>{nome_interrogatorio}</a>"
pagina += "<hr>"

freq = dict()
for entrada in dicionario:
	if not dicionario[entrada] in freq: freq[dicionario[entrada]] = 1
	else: freq[dicionario[entrada]] += 1
lista_freq = list()
for entrada in freq:
	lista_freq.append((entrada, freq[entrada]))

expressao = form['expressao'].value.replace("'", '"')

identificador = expressao.split(" ")[1] if not " @" in expressao else expressao.rsplit(" @", 1)[1].split(" ")[0]
identificador = "token." + identificador
identificador = identificador.replace("token.token", "token")
identificador = identificador.rsplit(".", 1)[0]
if expressao[0] == "@": expressao = expressao[1:]

with open("dist.log", 'w') as f:
	f.write("\n".join([identificador, expressao]))

pagina += f"<br><table style='border-spacing: 20px 0px; margin-left:0px; text-align:left'><th>#</th><th>{form['coluna'].value}</th><th>frequência</th><th>%</th>"
for i, entrada in enumerate(sorted(lista, key=lambda x: (-x[1], x[0]))):
	entradaEscapada = re.escape(entrada[0])
	pagina += f"<tr><td>{i+1}</td><td><a target='_blank' href='../cgi-bin/interrogar.cgi?go=True&corpus={form['corpus'].value}&params={encodeUrl(expressao.replace(' @', ' '))} and @{identificador}.{form['coluna'].value} == \"{encodeUrl(entradaEscapada)}\"' title='Buscar casos: {expressao.replace(' @', ' ')} and @{identificador}.{form['coluna'].value} == \"{entradaEscapada}\"' style='text-decoration: none; color:blue;'>" + cgi.escape(entrada[0]) + "</a></td><td>" + str(entrada[1]) + "</td><td>"+str((entrada[1]/len(dist))*100)+"%</td></tr>"
pagina += "</table>"

'''
pagina += "<br><br><table style='border-spacing: 20px 0px;'><tr><th>#</th><th>"+form["coluna"].value+" diferentes</th></tr>"
for entrada in sorted(lista_freq, key=lambda x: (x[1], x[0]), reverse=True):
	pagina += "<tr><td>" + str(entrada[0]) + "</td><td>" + str(entrada[1]) + "</td></tr>"
pagina += "</table>"
'''

print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body>' + pagina + '<br><br></body>') #window.location="' + form['html'].value


