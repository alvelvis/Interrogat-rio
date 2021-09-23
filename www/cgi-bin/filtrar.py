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
from functions import fromInterrogarToHtml, cleanEstruturaUD
import html as web
import sys
import dill as pickle

from estrutura_dados import slugify as slugify

form = cgi.FieldStorage()

if not 'pesquisa' in form and not 'action' in form:
	html = '<head><title class="translateHtml">Filtrar: Interrogatório</title></head>'
	html += '<body><form action="../cgi-bin/filtrar.py" method=POST>'
	html += '<select name="html">'
	for arquivo in os.listdir('./interrogar-ud/resultados'):
		if os.path.isfile('./interrogar-ud/resultados/' + arquivo):
			html += '<option value="' + arquivo.rsplit('.', 1)[0] + '">' + arquivo.rsplit('.', 1)[0] + '</option>'
	html += '</select><br><select name="udoriginal">'
	for arquivo in os.listdir('./interrogar-ud/conllu'):
		if os.path.isfile('./interrogar-ud/conllu/' + arquivo):
			html += '<option value="' + arquivo + '">' + arquivo + '</option>'
	html += '</select><br><br><input type="text" name="pesquisa" placeholder="Expressão do filtro"><br><input type="text" placeholder="Nome do filtro" name="nome_pesquisa"><br><br><input type="submit" class="translateVal" value="Filtrar">'
	html += '</form></body>'
	print(html)

elif not 'action' in form: #or form['action'].value not in ['desfazer', 'view', 'remove']:

	if LOGIN:
		if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
			html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
			print(html)
			exit()

	pesquisa = form['pesquisa'].value.strip()
	if re.search(r'^\d+$', pesquisa.split(' ')[0]):
		criterio = pesquisa.split(' ')[0]
		parametros = pesquisa.split(' ', 1)[1]
	elif any(x in pesquisa for x in [' == ', ' = ', ' != ', ' !== ', ' === ']) and len(pesquisa.split('"')) > 2:
		criterio = '5'
		parametros = pesquisa
	else:
		criterio = '1'
		parametros = pesquisa
	
	if int(criterio) > int(open('./interrogar-ud/max_crit.txt', 'r').read().split()[0]):
		print('em desenvolvimento')
		exit()

	data = str(datetime.now()).replace(' ', '_').split('.')[0]
	ud = form['udoriginal'].value
	pagina_html = form['html'].value
	pesquisa_original = form['pesquisa_original'].value

	if os.path.isfile('./cgi-bin/json/' + slugify(ud + "_" + pesquisa_original.split(" ", 1)[1] + ".json")):
		with open("./cgi-bin/json/" + slugify(ud + "_" + pesquisa_original.split(" ", 1)[1] + ".json")) as f:
			busca_original = json.load(f)
	else:
		busca_original = interrogar_UD.main('./interrogar-ud/conllu/' + ud, int(pesquisa_original.split(" ", 1)[0]), pesquisa_original.split(" ", 1)[1], fastSearch=True)
	busca_original = [cleanEstruturaUD(x['resultado'].split("# sent_id = ")[1].split("\n")[0]) for x in busca_original['output']]
	
	if not 'nome_pesquisa' in form:
		nome_filtro = form['pesquisa'].value.replace('<b>', '').replace('</b>', '').replace('<font color=' + tabela['yellow'] + '>', '').replace('<font color=' + tabela['red'] + '>', '').replace('<font color=' + tabela['cyan'] + '>', '').replace('<font color=' + tabela['blue'] + '>', '').replace('<font color=' + tabela['purple'] + '>', '').replace('</font>', '').strip()
	else:
		nome_filtro = form['nome_pesquisa'].value.strip()

	resultados = interrogar_UD.main('./interrogar-ud/conllu/' + ud, int(criterio), parametros)
	if not os.path.isdir('./cgi-bin/json'):
		os.mkdir('./cgi-bin/json')
	try:
		with open("./cgi-bin/json/" + slugify(ud + "_" + parametros + ".p"), "wb") as f:
			pickle.dump(resultados, f)
	except Exception as e:
		sys.stderr.write("=> " + str(e))
		pass

	if os.path.isfile("./cgi-bin/filtros.json"):
		with open("./cgi-bin/filtros.json", "r") as f:
			filtros = json.load(f)
	else:
		filtros = {}
		
	if not pagina_html in filtros:
		filtros[pagina_html] = {'ud': ud, 'filtros': {}}
	if not nome_filtro in filtros[pagina_html]['filtros']:
		filtros[pagina_html]['filtros'][nome_filtro] = {'parametros': [], 'sentences': []}
	filtros[pagina_html]['filtros'][nome_filtro]['sentences'].extend([y for y in [x['resultadoEstruturado'].sent_id for x in resultados['output']] if y in busca_original and y not in [k for filtro in filtros[pagina_html]['filtros'] for k in filtros[pagina_html]['filtros'][filtro]['sentences']]])
	filtros[pagina_html]['filtros'][nome_filtro]['parametros'].append(criterio + ' ' + parametros)

	with open("./cgi-bin/filtros.json", "w") as f:
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

	with open("./cgi-bin/filtros.json") as f:
		filtros = json.load(f)

	filtros[nome_html]['filtros'].pop(nome_filtro)

	with open("./cgi-bin/filtros.json", "w") as f:
		json.dump(filtros, f)

	print(f"Filtro desfeito, feche esta janela.")#//window.location = '../interrogar-ud/resultados/{nome_html}.html'

elif form['action'].value == 'view':
	nome_html = form['html'].value
	nome_filtro = form['filtro'].value

	with open("./cgi-bin/filtros.json") as f:
		filtros = json.load(f)

	num_filtros = len(filtros[nome_html]['filtros'][nome_filtro]['sentences'])
	ud = filtros[nome_html]['ud']
	parametros = "\n<br>".join(filtros[nome_html]['filtros'][nome_filtro]['parametros'])
	sentences = filtros[nome_html]['filtros'][nome_filtro]['sentences']

	html = '<script src="../interrogar-ud/jquery-latest.js"></script>'
	html += '<script src="../interrogar-ud/resultados.js"></script>'
	html += "<title>{title}</title><h1>{nome_filtro} (<span class='len_filtros'>{len_filtros}</span>)</h1><a title='Todas as sentenças voltarão para a busca inicial' class='translateTitle translateHtml' style='cursor:pointer; color:blue; text-decoration: underline;' onclick='if(window.confirm(\"Deseja desfazer o filtro?\")) {{ window.location.href = \"../cgi-bin/filtrar.py?action=desfazer&html={nome_html}&filtro={nome_filtro_encoded}\"; }}'>[Desfazer filtro]</a> <a href='#' class='translateHtml' onclick='window.close()'>[Fechar página]</a><br><br>{parametros}<br><br><span class='translateHtml'>Busca inicial:</span> <a href='../interrogar-ud/resultados/{nome_html}.html'>{nome_html}</a><br><span class='translateHtml'>Corpus:</span> <a href='../interrogar-ud/conllu/{ud}' download>{ud}</a><br><br>".format(
		title=nome_filtro + ' (' + str(num_filtros) + ') - Interrogatório',
		nome_filtro=web.escape(nome_filtro),
		nome_filtro_encoded = functions.encodeUrl(nome_filtro),
		len_filtros=num_filtros,
		nome_html=nome_html,
		ud=ud,
		parametros=parametros,
	)

	resultados = []
	sentences_ja_filtrados = []
	for parametros in filtros[nome_html]['filtros'][nome_filtro]['parametros']:
		if os.path.isfile('./cgi-bin/json/' + slugify(ud + "_" + parametros.split(" ", 1)[1] + ".p")):
			with open("./cgi-bin/json/" + slugify(ud + "_" + parametros.split(" ", 1)[1] + ".p"), "rb") as f:
				busca = pickle.load(f)
		else:
			busca = interrogar_UD.main(f"./interrogar-ud/conllu/{ud}", int(parametros.split(" ", 1)[0]), parametros.split(" ", 1)[1])
		for x in busca['sentences']:
			if x in sentences and x not in sentences_ja_filtrados:
				resultados.append(busca['output'][busca['sentences'][x]]['resultadoAnotado'])
				sentences_ja_filtrados.append(x)
	
	total = len(resultados)
	for i, resultado in enumerate(resultados):
		html += '<div class="sentence"><a onclick=\'removeFromFilter($(this), "{sentence}", "{html}", "{filtro}")\' class="translateTitle" title="Retornar esta sentença para a busca inicial" style="cursor:pointer; text-decoration:none;"><font color="red">[x]</font></a> <b>{agora} / {maximo} - {sentence}</b><br><span style="cursor:pointer;" class="translateTitle" title="Clique para mostrar a anotação" onclick="$(this).siblings(\'.anno\').toggle();">{text}</span><pre style="display:none" class="anno">{anno}</pre>'.format(
			sentence=cleanEstruturaUD(fromInterrogarToHtml(resultado.sent_id)).strip(),
			text=fromInterrogarToHtml(resultado.metadados['clean_text'] if 'clean_text' in resultado.metadados else resultado.text),
			html=nome_html,
			filtro=web.escape(nome_filtro.replace('"', "&quot;")),
			agora=i+1,
			maximo=total,
			anno=fromInterrogarToHtml(resultado.tokens_to_str()),
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

	with open("./cgi-bin/filtros.json") as f:
		filtros = json.load(f)

	filtros[nome_html]['filtros'][nome_filtro]['sentences'] = [x for x in filtros[nome_html]['filtros'][nome_filtro]['sentences'] if x not in [forbidden_sent_id]]

	with open("./cgi-bin/filtros.json", "w") as f:
		json.dump(filtros, f)

	print("<script>window.history.back(true);</script>")
