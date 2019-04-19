#!/usr/bin/python3
# -*- coding: UTF-8 -*-

#import cookies
import os

#if not 'HTTP_COOKIE' in os.environ: os.environ['HTTP_COOKIE'] = ''
#cookie = cookies.Cookie(os.environ['HTTP_COOKIE'])

#print(cookie)
print("Content-type:text/html")
print('\n\n')

import sys
import cgi,cgitb
cgitb.enable()
import re

#conectado = False
#if 'conectado' in cookie and cookie['conectado'] == True: conectado = True

def printar(coluna = '', valor = ''):
	from estrutura_dados import slugify as slugify
	html = open('/interrogar-ud/index1.html', 'r').read()

	if not os.path.isfile('/interrogar-ud/queries.txt'): open('/interrogar-ud/queries.txt', 'w').write('')
	queries = open('/interrogar-ud/queries.txt', 'r').read().splitlines()
	queries = [x for x in queries if x.strip() != '']

	novo_html = ''

	criterios = open('/interrogar-ud/criterios.txt', 'r').read().split('!@#')

	novo_html += '<form id=pesquisa action="/cgi-bin/interrogatorio.cgi" method="POST"><table><tr><td style="padding-bottom:0px; margin-bottom:0px;">Filtrar pesquisas:</td></tr><tr><td style="padding-right:0px;"><select id=coluna name="coluna" required><option value=":">Tudo</option><option value="1">Nome</option><option value="3">Critério de busca</option><option value="4">Expressão de busca</option><option value="5">CoNLLU</option><option value="6">Data</option></select></td><td style="width:100%"><input type=text style="width:100%; max-width:100%;" id=valor name=valor value="' + valor + '" autofocus=true required></td><td style="padding-left:0px;"><input type=submit class="btn-gradient mini orange" value="Realizar filtro" style="display:inline-block">'

	if coluna: novo_html += ' <center><a style="display:inline-block" class="close-thik" href="/cgi-bin/interrogatorio.cgi">Cancelar </a></center>'

	novo_html += '</td></tr></table></form><br>'
	html_query = ''
	total = 0
	for query in queries:
		if query.strip():
			if (coluna != ':' and valor and len(query.split('\t')) >= int(coluna) + 1 and (re.search(valor, query.split('\t')[int(coluna)], flags=re.I|re.M))) or (not coluna) or (coluna == ':' and re.search(valor, query, flags=re.I|re.M)):
				filtros = ''
				try:
					if os.path.isdir(query.split('\t')[0].rsplit('.html', 1)[0]):
						filtros = '<b>Filtros:</b><br>'
						for arquivo in os.listdir(query.split('\t')[0].rsplit('.html', 1)[0]):
							if not '_anterior' in arquivo:
								filtros += '<a href="''' + query.split('\t')[0].rsplit('.html', 1)[0] + '/' + arquivo + '">' + open(query.split('\t')[0].rsplit('.html', 1)[0] + '/' + arquivo, 'r').read().split('<h1>')[1].split('1>')[0].split('>', 1)[1].rsplit('</h', 1)[0].replace('</span>', '') + '</a><br>'
				except: pass
				html_query += '''<div class="container-lr"><table><tr><td style="padding-top:0px; padding-bottom:0px;"><p style="padding-top:0px; padding-bottom:0px;"><h3><a href="''' + query.split('\t')[0] + '''">''' + query.split('\t')[1].replace('<','&lt;').replace('>','&gt;') + ''' (''' + query.split('\t')[2] + ''')</a> <!--a class="close-thik" href="#" onclick='apagar("''' + query.split('\t')[0].split('resultados/')[1].split('.html')[0] + '''")'></a--></h3></p></td></tr></table><table><tr><td><div class="tooltip" style="display: inline-block">''' + query.split('\t')[3] + ''' ''' + query.split('\t')[4].replace('<','&lt;').replace('>','&gt;') + '''<span class="tooltiptext">''' + criterios[int(query.split('\t')[3])].split('<h4>')[0] + '''</span></div></td></tr><tr><td><a href="#" onclick="document.getElementById('coluna').value = '5'; document.getElementById('valor').value = \'''' + query.split('\t')[5] + '''\'; document.getElementById('pesquisa').submit();">''' + query.split('\t')[5] + '''</a><br>''' + query.split('\t')[6].replace('_', ' ') + '''</td><td>''' + filtros + '''</td></tr></table></div>\n'''
				# if conectado else '''<div class="container-lr" ><p><h3><a href="''' + query.split('\t')[0] + '''">''' + query.split('\t')[1].replace('<','&lt;').replace('>','&gt;') + ''' (''' + query.split('\t')[2] + ''')</a> <!--a class="close-thik" href="#" onclick='apagar("''' + query.split('\t')[0].split('resultados/')[1].split('.html')[0] + '''")'></a--></h3></p><p><div class="tooltip" style="display: inline-block">''' + query.split('\t')[3] + ''' ''' + query.split('\t')[4].replace('<','&lt;').replace('>','&gt;') + '''<span class="tooltiptext">''' + criterios[int(query.split('\t')[3])].split('<h4>')[0] + '''</span></div></p><small><p>''' + query.split('\t')[5] + '''</p><p>''' + query.split('\t')[6] + '''</p></small></div>\n''' # &nbsp;&nbsp;&nbsp;&nbsp;
				total += 1

	novo_html = html.split('<!--SPLIT-->')[0] + novo_html + 'Interrogações: ' + str(total) + '<br><br>' + html_query + html.split('<!--SPLIT-->')[1]

	print(novo_html)

if os.environ['REQUEST_METHOD'] != 'POST':
	printar()
else:
	form = cgi.FieldStorage()
	coluna = form['coluna'].value
	valor = form['valor'].value
	printar(coluna, valor)
