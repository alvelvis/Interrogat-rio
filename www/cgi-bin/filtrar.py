#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import os
import cgi,cgitb
cgitb.enable()
import re
import interrogar_UD
import functions
from functions import tabela
import json
from credenciar import LOGIN
from functions import fromInterrogarToHtml, cleanEstruturaUD
import html as web
import sys

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
	from api import filtrar
	if LOGIN:
		if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
			html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
			print(html)
			exit()
	filtrar(form)

elif form['action'].value == 'desfazer':
	
	if LOGIN:
		if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
			html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
			print(html)
			exit()

	nome_html = form['html'].value
	nome_filtro = form['filtro'].value

	with open("./cgi-bin/json/filtros.json") as f:
		filtros = json.load(f)

	with open("./cgi-bin/json/query_records.json") as f:
		query_records = json.loads(f.read())
	for parametro in filtros[nome_html]['filtros'][nome_filtro]['parametros']:
		query_records[parametro['json_id']]['persistent'] = False
	with open("./cgi-bin/json/query_records.json", "w") as f:
		f.write(json.dumps(query_records))

	filtros[nome_html]['filtros'].pop(nome_filtro)

	with open("./cgi-bin/json/filtros.json", "w") as f:
		json.dump(filtros, f)

	print(f"Filtro desfeito, feche esta janela.")#//window.location = '../interrogar-ud/resultados/{nome_html}.html'

elif form['action'].value == 'view':
	nome_html = form['html'].value
	nome_filtro = form['filtro'].value

	with open("./cgi-bin/json/filtros.json") as f:
		filtros = json.load(f)

	num_filtros = len(filtros[nome_html]['filtros'][nome_filtro]['sentences'])
	ud = filtros[nome_html]['ud']
	parametros = "\n<br>".join([x['parametro'] for x in filtros[nome_html]['filtros'][nome_filtro]['parametros']])
	sentences = filtros[nome_html]['filtros'][nome_filtro]['sentences']

	html = '<script src="../interrogar-ud/jquery-latest.js"></script>'
	html += '<script src="../interrogar-ud/resultados.js"></script>'
	html += "<title>{title}</title><h1>{nome_filtro} (<span class='len_filtros'>{len_filtros}</span>)</h1>\
		<a title='Mostrar lista de sent_id das frases' class='translateTitle translateHtml extractSentidFilter' style='cursor:pointer; color:blue; text-decoration: underline;'>[Lista de sent_id]</a> \
		<a title='Todas as sentenças voltarão para a busca inicial' class='translateTitle translateHtml' style='cursor:pointer; color:blue; text-decoration: underline;' onclick='if(window.confirm(\"Deseja desfazer o filtro?\")) {{ window.location.href = \"../cgi-bin/filtrar.py?action=desfazer&html={nome_html}&filtro={nome_filtro_encoded}\"; }}'>[Desfazer filtro]</a> \
		<!--a href='#' class='translateHtml' onclick='window.close()'>[Fechar página]</a>\
		<br--><span class='extractSentidSpan' style='display:none'></span><input class='extractSentidInput' style='width: 300px; display:none; margin:5px;'>\
		<br>{parametros}<br><br>\
		<span class='translateHtml'>Busca inicial:</span> <a href='../interrogar-ud/resultados/{nome_html}.html'>{nome_html}</a><br>\
		<span class='translateHtml'>Corpus:</span> <a href='../interrogar-ud/conllu/{ud}' download>{ud}</a><br><br>".format(
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
	for parametro in filtros[nome_html]['filtros'][nome_filtro]['parametros']:
		json_id = parametro['json_id']
		with open("./cgi-bin/json/%s.json" % json_id) as f:
			busca = json.load(f)
		#busca = interrogar_UD.main(f"./interrogar-ud/conllu/{ud}", int(parametros.split(" ", 1)[0]), parametros.split(" ", 1)[1])
		for x in busca['sentences']:
			if x in sentences and x not in sentences_ja_filtrados:
				resultados.append(busca['output'][busca['sentences'][x]]['resultado'])
				sentences_ja_filtrados.append(x)
	
	total = len(resultados)
	for i, resultado in enumerate(resultados):
		sent_id = resultado.split("# sent_id = ")[1].split("\n")[0]
		text = resultado.split("# %s = " % ("clean_text" if "# clean_text = " in resultado else "text"))[1].split("\n")[0]
		html += '<div class="sentence"><a onclick=\'removeFromFilter($(this), "{sentence}", "{html}", "{filtro}")\' class="translateTitle" title="Retornar esta sentença para a busca inicial" style="cursor:pointer; text-decoration:none;"><font color="red">[x]</font></a> <b>{agora} / {maximo} - <span class="sent_id">{sentence}</span></b><br><span style="cursor:pointer;" class="translateTitle" title="Clique para mostrar a anotação" onclick="$(this).siblings(\'.anno\').toggle();">{text}</span><pre style="display:none" class="anno">{anno}</pre>'.format(
			sentence=cleanEstruturaUD(fromInterrogarToHtml(sent_id)).strip(),
			text=fromInterrogarToHtml(text),
			html=nome_html,
			filtro=web.escape(nome_filtro.replace('"', "&quot;")),
			agora=i+1,
			maximo=total,
			anno=fromInterrogarToHtml(resultado),
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

	with open("./cgi-bin/json/filtros.json") as f:
		filtros = json.load(f)

	filtros[nome_html]['filtros'][nome_filtro]['sentences'] = [x for x in filtros[nome_html]['filtros'][nome_filtro]['sentences'] if x not in [forbidden_sent_id]]

	with open("./cgi-bin/json/filtros.json", "w") as f:
		json.dump(filtros, f)

	print("<script>window.history.back(true);</script>")