#!/usr/bin/python3
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

if not 'pesquisa' in form and not 'action' in form:
	html = '<head><title>Filtrar: Interrogatório</title></head>'
	html += '<body><form action="../cgi-bin/filtrar.cgi" method=POST>'
	html += '<select name="html">'
	for arquivo in os.listdir('../interrogar-ud/resultados'):
		if os.path.isfile('../interrogar-ud/resultados/' + arquivo):
			html += '<option value="' + arquivo.rsplit('.', 1)[0] + '">' + arquivo.rsplit('.', 1)[0] + '</option>'
	html += '</select><br><select name="udoriginal">'
	for arquivo in os.listdir('../interrogar-ud/conllu'):
		if os.path.isfile('../interrogar-ud/conllu/' + arquivo):
			html += '<option value="' + arquivo + '">' + arquivo + '</option>'
	html += '</select><br><br><input type="text" name="pesquisa" placeholder="Expressão do filtro"><br><input type="text" placeholder="Nome do filtro" name="nome_pesquisa"><br><br><input type="submit" value="Filtrar">'
	html += '</form></body>'
	print(html)

elif not 'action' in form: #or form['action'].value not in ['desfazer', 'view', 'remove']:

	if LOGIN:
		if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
			html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
			print(html)
			exit()

	pesquisa = form['pesquisa'].value
	if re.search(r'^\d+$', pesquisa.split(' ')[0]):
		criterio = pesquisa.split(' ')[0]
		parametros = pesquisa.split(' ', 1)[1]
	elif any(x in pesquisa for x in [' == ', ' = ', ' != ', ' !== ', ' === ']):
		criterio = '5'
		parametros = pesquisa
	else:
		criterio = '1'
		parametros = pesquisa
	
	if int(criterio) > int(open('../interrogar-ud/max_crit.txt', 'r').read().split()[0]):
		print('em desenvolvimento')
		exit()

	data = str(datetime.now()).replace(' ', '_').split('.')[0]
	ud = form['udoriginal'].value
	pagina_html = form['html'].value
	
	if not 'nome_pesquisa' in form:
		nome_filtro = form['pesquisa'].value.replace('<b>', '').replace('</b>', '').replace('<font color=' + tabela['yellow'] + '>', '').replace('<font color=' + tabela['red'] + '>', '').replace('<font color=' + tabela['cyan'] + '>', '').replace('<font color=' + tabela['blue'] + '>', '').replace('<font color=' + tabela['purple'] + '>', '').replace('</font>', '')
	else:
		nome_filtro = form['nome_pesquisa'].value

	resultados = interrogar_UD.main('../interrogar-ud/conllu/' + ud, int(criterio), parametros)

	if os.path.isfile("../cgi-bin/filtros.json"):
		with open("../cgi-bin/filtros.json", "r") as f:
			filtros = json.load(f)
	else:
		filtros = {}
		
	if not pagina_html in filtros:
		filtros[pagina_html] = {'ud': ud, 'filtros': {}}
	if not nome_filtro in filtros[pagina_html]['filtros']:
		filtros[pagina_html]['filtros'][nome_filtro] = {'parametros': [], 'sentences': []}
	filtros[pagina_html]['filtros'][nome_filtro]['sentences'].extend([y for y in [x['resultadoEstruturado'].sent_id if 'sent_id' in x['resultadoEstruturado'].metadados else x['resultadoEstruturado'].text for x in resultados['output']] if y not in filtros[pagina_html]['filtros'][nome_filtro]['sentences']])
	filtros[pagina_html]['filtros'][nome_filtro]['parametros'].append(criterio + ' ' + parametros)

	with open("../cgi-bin/filtros.json", "w") as f:
		json.dump(filtros, f)
		
	print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body onload="redirect()"><script>function redirect() { window.location = "../interrogar-ud/resultados/' + form['html'].value + '.html" }</script></body>')

elif form['action'].value == 'desfazer':
	
	if LOGIN:
		if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
			html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
			print(html)
			exit()

	nome_html = form['html'].value
	nome_filtro = form['filtro'].value

	with open("../cgi-bin/filtros.json") as f:
		filtros = json.load(f)

	filtros[nome_html]['filtros'].pop(nome_filtro)

	with open("../cgi-bin/filtros.json", "w") as f:
		json.dump(filtros, f)

	print(f"<script>window.location = '../interrogar-ud/resultados/{nome_html}.html'</script>")

elif form['action'].value == 'view':
	nome_html = form['html'].value
	nome_filtro = form['filtro'].value

	with open("../cgi-bin/filtros.json") as f:
		filtros = json.load(f)

	num_filtros = len(filtros[nome_html]['filtros'][nome_filtro]['sentences'])
	ud = filtros[nome_html]['ud']
	parametros = "\n".join(filtros[nome_html]['filtros'][nome_filtro]['parametros'])
	sentences = filtros[nome_html]['filtros'][nome_filtro]['sentences']

	html = '<script src="../interrogar-ud/jquery-latest.js"></script>'
	html += "<title>{title}</title><h1>{nome_filtro} (<span class='len_filtros'>{len_filtros}</span>)</h1><a title='Todas as sentenças voltarão para a busca inicial' href='../cgi-bin/filtrar.cgi?action=desfazer&html={nome_html}&filtro={nome_filtro}'>[Desfazer filtro]</a> <a href='#' onclick='window.close()'>[Fechar página]</a><br><br>{parametros}<br><br>Busca inicial: <a href='../interrogar-ud/resultados/{nome_html}.html'>{nome_html}</a><br>Corpus: <a href='../interrogar-ud/conllu/{ud}' download>{ud}</a><br><br>".format(
		title=nome_filtro + ' (' + str(num_filtros) + ') - Interrogatório',
		nome_filtro=nome_filtro,
		len_filtros=num_filtros,
		nome_html=nome_html,
		ud=ud,
		parametros=parametros,
	)

	corpus = estrutura_ud.Corpus(recursivo=False)
	corpus.load(f"../interrogar-ud/conllu/{ud}")
	for sentence in sentences:
		html += '<div class="sentence"><a onclick="$(this).parents(\'.sentence\').remove(); $(\'.len_filtros\').html(parseInt($(\'.len_filtros\').html())-1); window.location=\'../cgi-bin/filtrar.cgi?action=remove&s={sentence}&html={html}&filtro={filtro}\'" title="Retornar esta sentença para a busca inicial" style="cursor:pointer"><font color="red">[x]</font></a> <b>{sentence}</b>: {text}'.format(
			sentence=corpus.sentences[sentence].sent_id, 
			text=corpus.sentences[sentence].text,
			html=nome_html,
			filtro=nome_filtro,
			)
		html += "<hr></div>"

	html += "<br><br>"
	print(html)

elif form['action'].value == 'remove':
	if LOGIN:
		if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
			html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
			print(html)
			exit()

	nome_html = form['html'].value
	nome_filtro = form['filtro'].value
	forbidden_sent_id = form['s'].value

	with open("../cgi-bin/filtros.json") as f:
		filtros = json.load(f)

	filtros[nome_html]['filtros'][nome_filtro]['sentences'] = [x for x in filtros[nome_html]['filtros'][nome_filtro]['sentences'] if x not in [forbidden_sent_id]]

	with open("../cgi-bin/filtros.json", "w") as f:
		json.dump(filtros, f)

	print("<script>window.history.back(true);</script>")
