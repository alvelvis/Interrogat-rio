#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#import cookies
import os

#if not 'HTTP_COOKIE' in os.environ: os.environ['HTTP_COOKIE'] = ''
#cookie = cookies.Cookie(os.environ['HTTP_COOKIE'])

#print(cookie)
print("Content-type:text/html; charset=utf-8")
print('\n\n')

import sys
import cgi,cgitb
cgitb.enable()
import re, html, time
from functions import prettyDate, encodeUrl
import json
import html as web
from datetime import datetime

#conectado = False
#if 'conectado' in cookie and cookie['conectado'] == True: conectado = True

def printar(coluna = '', valor = ''):
	from estrutura_dados import slugify as slugify
	with open('../interrogar-ud/index1.html', 'r') as f:
		html = f.read()

	if not os.path.isfile('../interrogar-ud/queries.txt'):
		with open('../interrogar-ud/queries.txt', 'w') as f:
			f.write('')
	with open('../interrogar-ud/queries.txt', 'r') as f:
		queries = f.read().splitlines()
	queries = [x for x in queries if x.strip() != '']

	novo_html = ''

	with open('../interrogar-ud/criterios.txt', 'r') as f:
		criterios = f.read().split('!@#')
	criterios = [x for x in criterios if x.strip()]

	novo_html += '<form id=pesquisa action="../cgi-bin/interrogatorio.cgi" method="POST"><table><tr><td style="padding-bottom:0px; margin-bottom:0px;" class="translateHtml">Filtrar buscas:</td></tr><tr><td style="padding-right:0px;"><select id=coluna name="coluna" required><option value=":" class="translateHtml">Tudo</option><option value="1" class="translateHtml">Nome</option><option value="3" class="translateHtml">Critério de busca</option><option value="4" class="translateHtml">Expressão de busca</option><option value="5" class="translateHtml">CoNLL-U</option><option value="6" class="translateHtml">Data</option></select></td><td style="width:100%"><input type=text style="width:100%; max-width:100%;" id=valor name=valor value="' + valor + '" class="interrogatorioSearch" autofocus=true required></td><td style="padding-left:0px;"><input type=submit class="btn-gradient mini orange translateVal" value="Realizar filtro" style="display:inline-block">'

	if coluna: novo_html += ' <center><a style="display:inline-block" class="close-thik translateHtml" href="../cgi-bin/interrogatorio.cgi">Cancelar </a></center>'

	novo_html += '</td></tr></table></form><br>'

	for arquivo in os.listdir("../interrogar-ud/inProgress"):
		if arquivo != "README.txt":
			if int(str(datetime.now()).split(" ")[0].split("-")[2]) != int(str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime("../interrogar-ud/inProgress/" + arquivo)))).split(" ")[0].split("-")[2]) or int(str(datetime.now()).split(" ")[1].split(":")[0]) > int(str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime("../interrogar-ud/inProgress/" + arquivo)))).split(" ")[1].split(":")[0]) + 2:
				os.remove("../interrogar-ud/inProgress/" + arquivo)

	inProgress = ["<tr><td>" + prettyDate(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime("../interrogar-ud/inProgress/" + x)))).beautifyDateDMAH() + "</td><td>" + x.split(" ", 1)[1].rsplit(' ', 1)[0] + "</td><td>" + x.split(" ", 1)[0] + "</td></tr>" for x in os.listdir('../interrogar-ud/inProgress/') if x.endswith('.inProgress')]
	if inProgress:
		html = html.replace("<title class=\"translateHtml\">", f"<title class='translateHtml'>{len(inProgress)} busca{'s' if len(inProgress) > 1 else ''} em progresso - ")
		novo_html += "<h2 class='translateHtml'>Buscas em progresso:</h2><small><a href='javascript:location.reload()' class='translateHtml'>Atualizar</a></small><div class=\"container-lr\"><table>{0}</table></div>".format(''.join(inProgress)) + "<br>"

	filtros_json = []
	if os.path.isfile("../cgi-bin/filtros.json"):
		with open("../cgi-bin/filtros.json") as f:
			filtros_json = json.load(f)

	html_query = ''
	total = 0
	for query in queries:
		if query.strip():
			if (coluna != ':' and valor and len(query.split('\t')) >= int(coluna) + 1 and (re.search(valor, query.split('\t')[int(coluna)], flags=re.I|re.M))) or (not coluna) or (coluna == ':' and re.search(valor, query, flags=re.I|re.M)):
				filtros = ''
				if query.split('\t')[0].rsplit('.html', 1)[0].rsplit("/", 1)[1] in filtros_json:
					filtros = '<b>Filtros (' + str(len([x for filtro in filtros_json[query.split('\t')[0].rsplit('.html', 1)[0].rsplit("/", 1)[1]]['filtros'] for x in filtros_json[query.split('\t')[0].rsplit('.html', 1)[0].rsplit("/", 1)[1]]['filtros'][filtro]['sentences']])) + '):</b><br>'
					for filtro in filtros_json[query.split('\t')[0].rsplit('.html', 1)[0].rsplit("/", 1)[1]]['filtros']:
						filtros += '<a target="_blank" href=\'../cgi-bin/filtrar.cgi?action=view&html=' + query.split('\t')[0].rsplit('.html', 1)[0].rsplit("/", 1)[1] + '&filtro=' + encodeUrl(filtro) + '\'>' + filtro + ' ('+ str(len(filtros_json[query.split('\t')[0].rsplit('.html', 1)[0].rsplit("/", 1)[1]]['filtros'][filtro]['sentences'])) + ')</a><br>'
				html_query += '''<div class="container-lr"><table style="width:100%"><tr><td style="padding-top:0px; padding-bottom:0px; max-width: 60%; word-wrap: break-word;"><p style="padding-top:0px; padding-bottom:0px; max-width: 60%; word-wrap: break-word;"><h3><a href="''' + query.split('\t')[0] + '''">''' + query.split('\t')[1].replace('<','&lt;').replace('>','&gt;') + ''' (''' + query.split('\t')[2] + ''')</a> <!--a class="close-thik" href="#" onclick='apagar("''' + query.split('\t')[0].split('resultados/')[1].split('.html')[0] + '''")'></a--></h3></p></td></tr></table><table style="width:100%"><tr><td colspan="2" style="word-wrap: break-word;"><div style="word-wrap: break-word; display: inline-block;">''' + query.split('\t')[3] + ''' ''' + query.split('\t')[4].replace('<','&lt;').replace('>','&gt;') + '''</div></td></tr><tr><td style="min-width: 50%; max-width:50%; word-wrap: break-word;"><a href="#" onclick="document.getElementById('coluna').value = '5'; document.getElementById('valor').value = \'''' + query.split('\t')[5] + '''\'; document.getElementById('pesquisa').submit();">''' + query.split('\t')[5] + '''</a><br><small>''' + prettyDate(query.split('\t')[6].replace("_", " ")).beautifyDateDMAH() + '''<br><a style="cursor:pointer;" onclick="if(window.confirm('Deseja apagar a busca?')) { window.location.href = '../cgi-bin/excluir_query.py?html=''' + query.split('\t')[0].rsplit('.html', 1)[0].rsplit("/", 1)[1] + ''''; }" class="translateHtml">excluir</a></small></td><td style="max-width: 50%; word-wrap: break-word;">''' + filtros + '''</td></tr></table></div>\n'''
				# if conectado else '''<div class="container-lr" ><p><h3><a href="''' + query.split('\t')[0] + '''">''' + query.split('\t')[1].replace('<','&lt;').replace('>','&gt;') + ''' (''' + query.split('\t')[2] + ''')</a> <!--a class="close-thik" href="#" onclick='apagar("''' + query.split('\t')[0].split('resultados/')[1].split('.html')[0] + '''")'></a--></h3></p><p><div class="tooltip" style="display: inline-block">''' + query.split('\t')[3] + ''' ''' + query.split('\t')[4].replace('<','&lt;').replace('>','&gt;') + '''<span class="tooltiptext">''' + criterios[int(query.split('\t')[3])].split('<h4>')[0] + '''</span></div></p><small><p>''' + query.split('\t')[5] + '''</p><p>''' + query.split('\t')[6] + '''</p></small></div>\n''' # &nbsp;&nbsp;&nbsp;&nbsp;
				total += 1

	novo_html = html.split('<!--SPLIT-->')[0] + novo_html + '<h2><span class="translateHtml">Buscas:</span> ' + str(total) + '</h2>' + html_query + html.split('<!--SPLIT-->')[1]

	print(novo_html)

if os.environ['REQUEST_METHOD'] != 'POST':
	printar()
else:
	form = cgi.FieldStorage()
	coluna = form['coluna'].value
	valor = form['valor'].value
	printar(coluna, valor)
