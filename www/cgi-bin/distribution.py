#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html")
print('\n\n')

fastSearch = ['teste', 'Busca rápida']

import os, sys
import cgi,cgitb
cgitb.enable()
import re
from datetime import datetime
from functions import tabela, prettyDate, encodeUrl, cleanEstruturaUD
import datetime
import html as web
import estrutura_ud
import interrogar_UD
import json

from estrutura_dados import slugify as slugify

different_distribution = ["dependentes", "children"]

#POST
form = cgi.FieldStorage()
if not 'corpus' in form:
	print("Corpus não selecionado.")
	exit()

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


dic_dist = interrogar_UD.getDistribution("../interrogar-ud/conllu/" + form['corpus'].value, form['notSaved'].value, filtros=filtros, coluna=form['coluna'].value)

pagina = '''
	<button onclick="topFunction()" id="myBtn" class="translateTitle translateHtml" title="Voltar ao topo">Voltar ao topo</button>
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
pagina += "<title>Distribuição de " + form["coluna"].value + ": Interrogatório</title>"
pagina += "<h1>Distribuição de " + form["coluna"].value + "</h1>"
pagina += '<a href="#" class="translateHtml" onclick="window.close()">Fechar</a><br><br><span class="translateHtml">Relatório gerado dia</span> ' + prettyDate(str(datetime.datetime.now())).beautifyDateDMAH() + ''
pagina += f"<hr><span class='translateHtml'>Busca:</span> <a href='../cgi-bin/interrogar.cgi?corpus={form['corpus'].value}&params={form['expressao'].value}'>" + form["expressao"].value + "</a><br>"
pagina += "<span class='translateHtml'>Corpus:</span></a> <a href='../interrogar-ud/conllu/"+form["corpus"].value+"' class='translateTitle' title='Baixar corpus' download>" + form["corpus"].value + "</a>"
pagina += "<br><br><span class='translateHtml'>Quantidade de ocorrências:</span></a> "+str(dic_dist["dist"])+"<br><span class='translateHtml'>Quantidade de</span> <b>"+form["coluna"].value+"</b> diferentes: "+str(len(dic_dist["lista"]))
if nome_interrogatorio and nome_interrogatorio not in fastSearch:
	pagina += f"<br><span class='translateHtml'>Busca salva em</span> <a href='../interrogar-ud/resultados/{link_interrogatorio}.html'>{nome_interrogatorio}</a>"
pagina += "<hr>"

expressao = form['expressao'].value.replace("'", '"')

identificador = expressao.split(" ")[1] if not " @" in expressao else expressao.rsplit(" @", 1)[1].split(" ")[0]
identificador = "token." + identificador
identificador = identificador.replace("token.token", "token")
identificador = identificador.rsplit(".", 1)[0]
if expressao[0] == "@": expressao = expressao[1:]

with open("dist.log", 'w') as f:
	f.write("\n".join([identificador, expressao]))

pagina += f"<br><table style='border-spacing: 20px 0px; margin-left:0px; text-align:left'><th>#</th><th>{form['coluna'].value}</th><th class='translateHtml'>frequência</th><th>%</th>"
for i, entrada in enumerate(sorted(dic_dist["lista"], key=lambda x: (-x[1], x[0]))):
	entradaEscapada = re.escape(entrada[0])
	if not form["coluna"].value in interrogar_UD.different_distribution:
		pagina += f"<tr><td>{i+1}</td><td><a target='_blank' href='../cgi-bin/interrogar.cgi?go=True&corpus={form['corpus'].value}&params={encodeUrl(expressao.replace(' @', ' '))} and @{identificador}.{form['coluna'].value} == \"{encodeUrl(entradaEscapada)}\"' title='Buscar casos: {expressao.replace(' @', ' ')} and @{identificador}.{form['coluna'].value} == \"{entradaEscapada}\"' style='text-decoration: none; color:blue;'>" + cgi.escape(entrada[0]) + "</a></td><td>" + str(entrada[1]) + "</td><td>"+str((entrada[1]/dic_dist["dist"])*100)+"%</td></tr>"
	elif form["coluna"].value in ["dependentes", "children"]:	
		sent_ids = []
		for sent_id in dic_dist["all_children"][entrada[0]]:
			sent_ids.append(f"# sent_id = {sent_id}")
		sent_ids = "1 (" + "|".join(sent_ids) + ")"
		pagina += f"<tr><td>{i+1}</td><td><a target='_blank' href='../cgi-bin/interrogar.cgi?go=True&corpus={form['corpus'].value}&params={encodeUrl(sent_ids)}' title='Buscar frases: {'|'.join(dic_dist['all_children'][entrada[0]])}' style='text-decoration: none; color:blue;'>" + entrada[0] + "</a></td><td>" + str(entrada[1]) + "</td><td>"+str((entrada[1]/dic_dist["dist"])*100)+"%</td></tr>"
pagina += "</table>"

'''
pagina += "<br><br><table style='border-spacing: 20px 0px;'><tr><th>#</th><th>"+form["coluna"].value+" diferentes</th></tr>"
for entrada in sorted(lista_freq, key=lambda x: (x[1], x[0]), reverse=True):
	pagina += "<tr><td>" + str(entrada[0]) + "</td><td>" + str(entrada[1]) + "</td></tr>"
pagina += "</table>"
'''

print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body>' + pagina + '<br><br></body>') #window.location="' + form['html'].value


