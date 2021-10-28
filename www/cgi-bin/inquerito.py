#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

print('Content-type:text/html; charset=utf-8')
print('\n\n')

import sys
import cgi, cgitb
cgitb.enable()
import time
import estrutura_dados
import estrutura_ud
import os
import shutil
from functions import prettyDate, cleanEstruturaUD
from datetime import datetime
from functions import corpusGenericoInquerito
import re
from subprocess import call
import html as web
import validar_UD
from credenciar import LOGIN
import interrogar_UD
import variables
import json

JULGAMENTO = False
if os.path.isdir("../Julgamento"):
    JULGAMENTO = "../Julgamento"
if os.path.isdir("../../Julgamento"):
    JULGAMENTO = "../../Julgamento"

form = cgi.FieldStorage()

if not os.path.isfile("./interrogar-ud/inqueritos_cars.txt"):
	with open("./interrogar-ud/inqueritos_cars.txt", "w") as f:
		f.write("")

if not os.path.isfile("./interrogar-ud/inqueritos.txt"):
	with open("./interrogar-ud/inqueritos.txt", "w") as f:
		f.write("")


mostrarEtiqueta = False
bosqueNaoEncontrado = corpusGenericoInquerito

arquivos = list()
for i, arquivo in enumerate(os.listdir('./interrogar-ud/conllu')):
	arquivos.append('<option value="'+arquivo+'">'+arquivo+'</option>')

with open('./interrogar-ud/inquerito.html', 'r') as f:
	html = f.read()
html = html.split('<select name="conllu">')[0] + '<select name="conllu">' + "\n".join(arquivos) + '</select>' + html.split('</select>')[1]

html1 = html.split('<!--SPLIT-->')[0]
html2 = html.split('<!--SPLIT-->')[1]

def get_head(frase, token):
	for linha in frase:
		if isinstance(linha, list) and token[6] == linha[0]:
			return ' (' + linha[1] + ')'
	return ''

def printar(coluna='', valor='', onlysent=False, managetags=False, tokenization_log=False):
	global html
	global html1
	global html2
	if valor and valor[0] == '#': valor = ''.join(valor[1:])

	html1 = html1.replace('<title class="translateHtml">Sistema de inquéritos</title>', '<title class="translateHtml">Relatório de inquéritos: Interrogatório</title>')

	html1 += '<hr><div id="div_filtro"><form name="form_pesquisa" id="form_pesquisa" action="../cgi-bin/inquerito.py?action=filtrar" method="POST"><span class="translateHtml">Filtrar relatório:</span><br><select name="coluna" id=coluna required><option value=":" class="translateHtml">Tudo</option><option value="6" class="translateHtml">Etiqueta</option><option value="0" class="translateHtml"># text</option><option value="7" class="translateHtml"># sent_id</option><option value="2" class="translateHtml">CoNLL-U</option><option value="3" class="translateHtml">Data</option><option value="4" class="translateHtml">Página no Interrogatório</option></select> <input type=text autofocus="true" name=valor id=valor value="' + valor.replace('"', '&quot;') + '" required> <input name="submit_search" class="translateVal" type=submit value="Realizar filtro" style="display:block-inline">'
	if coluna: html1 += ' <a style="display:block-inline" class="close-thik" href="../cgi-bin/inquerito.py"></a>'

	if tokenization_log:
		tokenization = {}
		if os.path.isfile("./cgi-bin/tokenization.json"):
			with open("./cgi-bin/tokenization.json") as f:
				tokenization = json.load(f)

		html1 += '</div>'
		for corpus in sorted(tokenization):
			html1 += '<div class="container">'
			html1 += '<h3><a href="#" title="Pesquisar pelo corpus" class="translateTitle" onclick="document.getElementById(\'coluna\').value=\'2\'; document.getElementById(\'valor\').value=\'' + corpus + '\'; document.getElementById(\'form_pesquisa\').submit();">{}</a></h3>'.format(corpus)
			for sent_id in sorted(tokenization[corpus]):
				html1 += f"<b><a title='Editar sentença' class='translateTitle' href='../cgi-bin/inquerito.py?conllu={corpus}&textheader={sent_id}&sentid={sent_id}'>{sent_id}</a></b>: {len(tokenization[corpus][sent_id])} <span class='translateHtml'>modificações de tokenização realizadas</span><br>"
			html1 += '</div>'
		html = html1 + html2
		return html

	html1 += '<br><br><input type=checkbox name=onlysent {}><a class="translateHtml" style="cursor:pointer" onclick="$(\'[name=onlysent]\').prop(\'checked\', !$(\'[name=onlysent]\').prop(\'checked\'));">Apenas sentenças</a>'.format('checked' if onlysent else '')

	if not "HTTP_HOST" in os.environ: os.environ["HTTP_HOST"] = "localhost:8000"
	html1 += '''</form><br><a href="../interrogar-ud/relatorio.txt" class="translateHtml" target="_blank">Baixar relatório</a>{} - <a class="translateHtml" href="../cgi-bin/inquerito.py?action=tokenization_log">Relatório de tokenização</a></div><hr>'''.format(' - <form style="display:inline-block" method="POST" id="managetags_form" action="../cgi-bin/inquerito.py"><input type=hidden name="action" value="manage_tags"><a style="cursor:pointer" class="translateHtml" onclick="managetags_form.submit()">Gerenciar etiquetas</a></form>' if mostrarEtiqueta else "")
	relatorio = str(datetime.now()).replace(' ', '_').split('.')[0] + '\nRelatório de Inquéritos - ' + os.environ['HTTP_HOST']
	if coluna: relatorio += '\nFiltro: ' + valor
	relatorio += '\nMostrando apenas as sentenças que foram alteradas' if onlysent else '\nMostrando todas as alterações em todas as sentenças'

	lista_sentences = list()
	relatorio42 = str()

	html1 += '<br><br>'

	if not os.path.isfile('./interrogar-ud/inqueritos.txt'):
		with open('./interrogar-ud/inqueritos.txt', 'w') as f:
			f.write('')

	html42 = ''
	total = 0
	javistos = list()
	with open('./interrogar-ud/inqueritos.txt', 'r') as f:
		inqueritos = f.read()
	for a, linha in enumerate(inqueritos.splitlines()):
		try:
			if linha.strip() != '':
				if not managetags:
					if (coluna != ':' and valor and len(linha.split('!@#')) > int(coluna) and (re.search(valor, linha.split('!@#')[int(coluna)], flags=re.I|re.M)) and linha.split('!@#')[int(coluna)] != 'NONE') or (not coluna) or (coluna == ':' and re.search(valor, linha, flags=re.I|re.M)):
						if (not onlysent) or (onlysent and not linha.split('!@#')[0] in javistos):
							html42 += '<div class="container"><form id="form_' + str(a) + '" action="../cgi-bin/inquerito.py" target="_blank" method="POST"><input name="textheader" type="hidden" value="' + linha.split('!@#')[0] + '"><input name="conllu" type="hidden" value="' + linha.split('!@#')[2] + '">'
							relatorio42 += '\n\n-------------------------'
							if len(linha.split('!@#')) >= 7 and linha.split('!@#')[6] != 'NONE':
								html42 += '<p><small><a href="#" onclick="document.getElementById(\'coluna\').value=\'6\'; document.getElementById(\'valor\').value=\'' + linha.split('!@#')[6].replace('"', '&quot;') + '\'; document.getElementById(\'form_pesquisa\').submit();">#' + linha.split('!@#')[6].replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<', '&lt;').replace('>', '&gt;').replace('@BOLD', '<b>').replace('/BOLD', '</b>') + '</a></small></p>'
								relatorio42 += '\n\n#' + linha.split('!@#')[6].replace('<b>', '').replace('</b>', '')
							html42 += '<p><h3><a style="cursor:pointer" onclick="form_' + str(a) + '.submit()">' + linha.split('!@#')[0] + '</a></h3></p>'
							relatorio42 += '\n\ntext = ' + linha.split('!@#')[0]
							if not '# text = ' + linha.split('!@#')[0] in lista_sentences: lista_sentences.append('# text = ' + linha.split('!@#')[0])
							if len(linha.split('!@#')) >= 8 and linha.split('!@#')[7] != 'NONE':
								html42 += '<p>sent_id = <a href="#" onclick="document.getElementById(\'coluna\').value=\'7\'; document.getElementById(\'valor\').value=\'' + linha.split('!@#')[7] + '\'; document.getElementById(\'form_pesquisa\').submit();">' + linha.split('!@#')[7] + '</a></p><input name="sentid" type="hidden" value="' + linha.split('!@#')[7] + '">'
								relatorio42 += '\nsent = ' + linha.split('!@#')[7]
							if len(linha.split('!@#')) >= 6 and linha.split('!@#')[4] != 'NONE' and linha.split('!@#')[5] != 'NONE':
								html42 = html42 + '<p>Página no Interrogatório: <a target="_blank" href="' + linha.split('!@#')[5] + '">' + web.escape(linha.split('!@#')[4]).replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<', '&lt;').replace('>', '&gt;').replace('@BOLD', '<b>').replace('/BOLD', '</b>') + '</a></p>'
								relatorio42 += '\n\nPágina no interrogatório: ' + web.escape(linha.split('!@#')[4]).replace('<b>', '').replace('</b>', '')
							if not onlysent:
								html42 += '<pre>ANTES:\t' + linha.split('!@#')[1].split(' --> ')[0].replace('<b>', '@BOLD').replace('</b>','/BOLD').replace('<','&lt;').replace('>','&gt;').replace('@BOLD', '<b>').replace('/BOLD', '</b>') + '</pre><pre>DEPOIS:\t' + linha.split('!@#')[1].split(' --> ')[1].replace('<b>','@BOLD').replace('</b>','/BOLD').replace('<','&lt;').replace('>','&gt;').replace('@BOLD', '<b>').replace('/BOLD', '</b>') + '</pre>'
								relatorio42 += '\n\nANTES:\t' + linha.split('!@#')[1].split(' --> ')[0].replace('<b>', '').replace('</b>','') + '\nDEPOIS:\t' + linha.split('!@#')[1].split(' --> ')[1].replace('<b>','').replace('</b>','')
							html42 += '<small><p><a href="#" onclick="document.getElementById(\'coluna\').value=\'2\'; document.getElementById(\'valor\').value=\'' + linha.split('!@#')[2] + '\'; document.getElementById(\'form_pesquisa\').submit();">' + linha.split("!@#")[2] + '</a></p><p>' + prettyDate(linha.split('!@#')[3].replace("_", ' ')).beautifyDateDMAH() + '</p></small></form></div>'
							relatorio42 += '\n\n' + linha.split('!@#')[2]
							relatorio42 += '\n' + linha.split('!@#')[3]
							total += 1
							javistos.append(linha.split('!@#')[0])
			
			elif managetags:
				if len(linha.split('!@#')) >= 7 and not linha.split('!@#')[6] in javistos and linha.split('!@#')[6] != 'NONE':
					html42 += '''<div class=container><form method="POST" action="../cgi-bin/inquerito.py"><input name="delete_tag" type=hidden value="''' + web.escape(linha.split('!@#')[6], quote=True) + '''"><a style="cursor:pointer" onclick="document.getElementsByName('coluna')[0].value = '6'; document.getElementsByName('valor')[0].value = \'''' + web.escape(linha.split('!@#')[6], quote=True) + '''\'; document.getElementsByName('form_pesquisa')[0].submit();">#''' + web.escape(linha.split('!@#')[6], quote=True) + '''</a> <a style="cursor:pointer" onclick="if (confirmar(\'''' + web.escape(linha.split('!@#')[6], quote=True) + '''\') == true) { this.parentNode.submit(); return false; }" class="close-thik"></a></form></div>'''
					total += 1
					javistos.append(linha.split('!@#')[6])
		except:
			sys.stderr.write('erro em inqueritos.txt: ' + linha)

	html = html1 + '<span class="translateHtml">Inquéritos</span>: ' + str(total) + '<br><br>' + html42 + html2
	with open('./interrogar-ud/relatorio.txt', 'w') as f:
		f.write(relatorio + '\n\n' + 'Inquéritos: ' + str(total) + '\n\nResumo: ' + str(len(lista_sentences)) + ' sentenças alteradas\n' + '\n'.join(lista_sentences) + relatorio42)
	return html

if (os.environ['REQUEST_METHOD'] == "POST") or ('textheader' in cgi.FieldStorage() and 'corpus' in cgi.FieldStorage()):
	if LOGIN:
		if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
			html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
			print(html)
			exit()
	else:
		pass

if os.environ['REQUEST_METHOD'] == "POST" and 'ud' in form.keys() and 'action' in form.keys() and form['action'].value == 'apagarCorpus':
	shutil.move('mv ./interrogar-ud/conllu/' + form['ud'].value, './interrogar-ud/tmp/')
	if JULGAMENTO:
		os.remove(f'{JULGAMENTO}/static/uploads/' + form['ud'].value.rsplit(".", 1)[0] + "_original.conllu")
	print('<script>window.location = "../cgi-bin/arquivo_ud.py"</script>')
	exit()

elif os.environ['REQUEST_METHOD'] == 'POST' and 'delete_tag' in form.keys():
	with open('./interrogar-ud/inqueritos.txt', 'r') as f:
		inqueritos = f.read()
	with open('./interrogar-ud/inqueritos_cars.txt', 'r') as f:
		tags = f.read()

	novo_inqueritos = list()
	for inquerito in inqueritos.splitlines():
		if len(inquerito.split('!@#')) >= 7 and inquerito.split('!@#')[6] == web.unescape(form['delete_tag'].value):
			continue
		else:
			novo_inqueritos.append(inquerito)

	novo_tags = list()
	for tag in tags.splitlines():
		if tag == web.unescape(form['delete_tag'].value):
			continue
		else:
			novo_tags.append(tag)

	with open('./interrogar-ud/inqueritos.txt', 'w') as f:
		f.write('\n'.join(novo_inqueritos))

	with open('./interrogar-ud/inqueritos_cars.txt', 'w') as f:
		f.write('\n'.join(novo_tags))

	html = '<script>window.location = "../cgi-bin/inquerito.py"</script>'
	print(html)


elif os.environ['REQUEST_METHOD'] == 'POST' and 'action' in form.keys() and form['action'].value == 'script':
	with open('./interrogar-ud/inqueritos.txt') as f:
		inqueritos = f.read().splitlines()

	nome_interrogatorio = form['nome_interrogatorio'].value
	link_interrogatorio = form['link_interrogatorio'].value.rsplit(".", 1)[0].rsplit("/", 1)[1]

	filtros = []
	if os.path.isfile("./cgi-bin/filtros.json"):
		with open("./cgi-bin/filtros.json") as f:
			filtros = json.load(f)
		if link_interrogatorio in filtros:
			filtros = [x for filtro in filtros[link_interrogatorio]['filtros'] for x in filtros[link_interrogatorio]['filtros'][filtro]['sentences']]
		else:
			filtros = []

	start = time.time()
	#pega os headers
	headers = list()
	for sentence in interrogar_UD.main('./interrogar-ud/conllu/' + form['conllu'].value, int(form['criterio'].value), form['parametros'].value, fastSearch=True)['output']:
		sent_id = re.sub(r"<.*?>", "", sentence['resultado'].split("# sent_id = ")[1].split("\n")[0])
		if not sent_id in filtros:
			headers.append(sent_id)
	#for sentence in interrogar_UD.main('./interrogar-ud/conllu/' + form['conllu'].value, int(form['criterio'].value), form['parametros'].value)['output']:
		#if sentence['resultadoEstruturado'].sent_id not in filtros:
			#headers.append("# text = " + sentence['resultadoEstruturado'].text)
	sys.stderr.write('\nheaders: {}'.format(time.time() - start))

	if form['executar'].value == 'sim':
		with open('./interrogar-ud/scripts/' + estrutura_dados.slugify(form['scriptName'].value), 'wb') as f:
			code = form['fileScript'].file.read()
			f.write(code)

	with open('./interrogar-ud/scripts/headers.txt', 'w') as f:
		f.write("\n".join(headers))
	
	start = time.time()
	if call('python3 "./interrogar-ud/scripts/MODELO-UD.py" ' + form['conllu'].value + ' ' + form['executar'].value + ' "' + estrutura_dados.slugify(form['scriptName'].value) + '"', shell=True):
		pass
	sys.stderr.write('\nMODELO-UD: {}'.format(time.time() - start))
	
	if form['executar'].value == 'exec':
		with open('./interrogar-ud/scripts/novos_inqueritos.txt', 'r') as f:
			novos_inqueritos = f.read().splitlines()
		for linha in novos_inqueritos:
			if form['nome_interrogatorio'] not in ['teste', 'Busca rápida']:
				inqueritos.insert(0, linha.rsplit('!@#', 1)[0] + '!@#' + form['nome_interrogatorio'].value + ' (' + form['occ'].value + ')!@#' + form['link_interrogatorio'].value + '!@#' + form['scriptName'].value + '!@#' + linha.rsplit('!@#', 1)[1])
			else:
				inqueritos.insert(0, linha.rsplit('!@#', 1)[0] + '!@#NONE!@#NONE!@#' + form['scriptName'].value + '!@#' + linha.rsplit('!@#', 1)[1])

		with open('./interrogar-ud/inqueritos_cars.txt', 'r') as f:
			cars = f.read().splitlines()
		if not form['scriptName'].value in cars:
			with open('./interrogar-ud/inqueritos_cars.txt', 'w') as f:
				f.write(form['scriptName'].value + '\n' + "\n".join(cars))

		with open('./interrogar-ud/inqueritos.txt', 'w') as f:
			f.write('\n'.join(inqueritos))
		html = '''<form id="submeter" action="../cgi-bin/inquerito.py?action=filtrar" method="POST"><input type=hidden name=coluna value=6><input type=hidden name=valor value="''' + form['scriptName'].value.replace('"', '&quot;') + '"></form>'
		html += '<script>document.getElementById("submeter").submit();</script>'

		os.remove('./interrogar-ud/conllu/' + form['conllu'].value)
		os.rename('./interrogar-ud/conllu/' + form['conllu'].value + '_script', './interrogar-ud/conllu/' + form['conllu'].value)
		os.remove('./interrogar-ud/scripts/novos_inqueritos.txt')
			
	elif form['executar'].value == 'sim':
		try:
			with open('./interrogar-ud/scripts/sim.txt', 'r') as f:
				sim = f.read()
		except:
			with open("./cgi-bin/error.log", "r") as f:
				file_errors = f.read()
			os.remove("./cgi-bin/error.log")
			print(file_errors.splitlines()[-1])
			exit()
		html = f'<title>Simulação de correção em lote: Interrogatório</title><h1>Simulação ({round(len(sim.splitlines())/4)})</h1>Verifique se as alterações estão adequadas e execute o script de correção no <a style="color:blue; cursor:pointer;" onclick="window.scrollTo(0,document.body.scrollHeight);">final da página</a>.\
		<br>Nome da correção: ' + form['scriptName'].value + '\
		<br>Corpus: <a target="_blank" href="../interrogar-ud/conllu/' + form['conllu'].value + '" download>' + form['conllu'].value + '</a>\
		<hr>'
		html += "<pre>" + sim + "</pre>"#.replace('<', '&lt;').replace('>', '&gt;')
		html += '<br><form action="../cgi-bin/inquerito.py?action=script&executar=exec" method="POST"><input type=hidden name=parametros value=\''+form['parametros'].value+'\'><input type=hidden name=criterio value=\"'+form['criterio'].value+'\"><input type=hidden name="nome_interrogatorio" value="''' + form['nome_interrogatorio'].value.replace('"', '&quot;') + '''"><input type=hidden name=occ value="''' + form['occ'].value + '''"><input type=hidden name="link_interrogatorio" value="''' + form['link_interrogatorio'].value + '''"><input type=hidden name="conllu" value="''' + form['conllu'].value + '''"><input type=hidden value="''' + form['scriptName'].value.replace('"', '&quot;') + '''" name="scriptName"><input type=submit value="Executar script"></form>'''
		os.remove('./interrogar-ud/scripts/sim.txt')

	os.remove('./interrogar-ud/scripts/headers.txt')
	print(html)

elif ((os.environ['REQUEST_METHOD'] == 'POST') or ('conllu' in form and 'textheader' in form)) and ((not 'action' in form.keys()) or ((form['action'].value != 'alterar' and form['action'].value != 'filtrar' and form['action'].value != 'script' and form['action'].value != 'manage_tags' and form['action'] != 'tokenization_log'))):
	html1 = html1.replace('<title class="translateHtml">Sistema de inquéritos</title>', '<title class="translateHtml">Novo inquérito: Interrogatório</title>') if not 'finalizado' in form else html1.replace('<title class="translateHtml">Sistema de inquéritos</title>', '<title class="translateHtml">Inquérito realizado com sucesso: Interrogatório</title>')
	ud = form['conllu'].value
	colored_ud = ud
	if not os.path.isfile('./interrogar-ud/conllu/' + ud):
		print(f"Corpus {ud} não encontrado.")
		exit()
		colored_ud = '<span style="background-color:red; color:white;">"' + ud + '" <span class="translateHtml">não encontrado</span></span>'
		ud = bosqueNaoEncontrado
	conlluzao = estrutura_dados.LerUD('./interrogar-ud/conllu/' + ud)
	if 'finalizado' in form:
		erros = []
		if 'sentid' in form:
			erros = validar_UD.validate('./interrogar-ud/conllu/' + ud, sent_id=form['sentid'].value, noMissingToken=True, errorList=variables.validar_UD)
		alertColor = "cyan" if not erros else "yellow"
		alertBut = "" if not erros else ", mas atenção:"
		html1 += f'<span style="background-color: {alertColor}"><span class="translateHtml">Alteração realizada com sucesso</span>{alertBut}</span>'
		if alertBut:
			html1 += "<ul>" 
			for erro in erros:
				html1 += f'<li>{erro}</li><ul>'
				for sentence in erros[erro]:
					if sentence and sentence['sentence']:
						html1 += f'''<li><a style="cursor:pointer" onclick="$('.id_{cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].id)}').focus();">{cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].id)} / {cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].word)}{' / ' + cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].__dict__[sentence['attribute']]) if sentence['attribute'] else ""}</a></li>'''
				html1 += "</ul>"
			html1 += "</ul>"
		html1 += '<br>'
	if 'tokenizado' in form:
		new_sentid = ""
		if form['tokenizado'].value != "True":
			new_sentid = form['tokenizado'].value
		if not new_sentid:
			html1 += f'<span style="background-color: cyan"><span class="translateHtml">Tokenização modificada com sucesso</span></span>'
		elif new_sentid:
			html1 += f'<span style="background-color: cyan"><span class="translateHtml">Tokenização modificada com sucesso</span></span><br><span style="background-color: yellow"><span class="translateHtml">Atenção: edite também o sent_id desta sentença e/ou a nova sentença:</span> <a href="../cgi-bin/inquerito.py?conllu={ud}&sentid={new_sentid}&textheader={new_sentid}" target="_blank">{new_sentid}</a></span>'
		html1 += "<br>"

	html1 = html1.split('<div class="header">')[0] + '<div class="header"><h1 class="translateHtml">Novo inquérito</h1><br><br>' + colored_ud + f'<br><br><a href="../cgi-bin/inquerito.py" class="translateHtml">Relatório de inquéritos</a> - <a href="../cgi-bin/contexto.py?corpus={ud}&sent_id={form["sentid"].value}" target="_blank" class="translateHtml">Mostrar contexto</a> - <form style="display:inline-block" target="_blank" method="POST" action="../cgi-bin/draw_tree.py?conllu=' + ud + '"><!--a href="#" onclick="this.parentNode.submit()" class="translateHtml">Visualizar árvore</a--><input type=hidden name=text value="' + form['textheader'].value + '"><input type=hidden name=sent_id value="' + form['sentid'].value + '"></form><a style="cursor:pointer;" onclick="window.close()" class="translateHtml endInquerito">Encerrar inquérito</a></div>' + html1.split('</div>', 3)[3]

	achou = False
	for i, sentence in enumerate(conlluzao):
		sentence2 = sentence
		for a, linha in enumerate(sentence2):
			if isinstance(linha, list):
				sentence2[a] = '\t'.join(sentence2[a])
		sentence2 = '\n'.join(sentence2)
		if '# text = ' in form['textheader'].value or '# sent_id = ' in form['textheader'].value:
			form['textheader'].value = form['textheader'].value.split(' = ', 1)[1]
		if ('# text = ' + form['textheader'].value + '\n' in sentence2) or ('# sent_id = ' + form['textheader'].value + '\n' in sentence2) or ('sentid' in form and '# sent_id = ' + form['sentid'].value + '\n' in sentence2):
			html1 += '<h3 class="translateHtml">Controles:</h3><span class="translateHtml">Esc: Encerrar inquérito</span><br><span class="translateHtml">Tab / Shift + Tab: ir para coluna à direita/esquerda</span><br><span class="translateHtml">↑ / ↓: ir para linha acima/abaixo</span><br><span class="translateHtml">↖: Arraste a coluna <b>dephead</b> de um token para a linha do token do qual ele depende</span><br><span class="translateHtml">Shift + Scroll: Mover tabela para os lados</span><br><br>'
			html1 += '<input style="display: inline-block; margin: 0px; cursor:pointer;" type="button" onclick="enviar()" class="translateVal btn-gradient blue small" id="sendAnnotation" value="Realizar alteração (Ctrl+Enter)"> '
			html1 += '<input style="display: inline-block; margin: 0px; cursor:pointer;" type="button" class="translateVal btn-gradient green small" id="changeTokenization" value="Modificar tokenização"><br><br>'
			html1 += '<!--br><br><br-->'

			html1 += '''<div class="divTokenization" style="display:none">
			<b class="translateHtml">Escolha que modificação deseja realizar:</b>
			<ul>
				<li><a class="translateHtml tokenizationMenu" style="cursor:pointer" onclick="$('.tokenization').hide(); $('.addToken').show();">Adicionar ou remover token</a></li>
				<li><a class="translateHtml tokenizationMenu" style="cursor:pointer" onclick="$('.tokenization').hide(); $('.mergeSentences').show();">Mesclar duas sentenças</a></li>
				<li><a class="translateHtml tokenizationMenu" style="cursor:pointer" onclick="$('.tokenization').hide(); $('.splitSentence').show();">Separar sentença em duas</a></li>
				<li><a class="translateHtml tokenizationMenu" style="cursor:pointer" id="modifySentid" corpus="{corpus_plain}" sent_id="{sent_id_plain}">Modificar sent_id</a></li>
				<li><a class="translateHtml tokenizationMenu" style="cursor:pointer" id="deleteSentence" corpus="{corpus_plain}" sent_id="{sent_id_plain}">Deletar sentença</a></li>
			</ul>
			<div class="addToken tokenization" style="display:none">
				<form action="../cgi-bin/tokenization.py?action=addToken" class="addTokenForm" method="POST">
					<select name="addTokenOption" class="addTokenOption">
						<option value="add" class="addTokenOptionSelect translateHtml">Adicionar token</option>
						<option value="rm" class="addTokenOptionSelect translateHtml">Remover token</option>
						<option value="addContraction" class="addTokenOptionSelect translateHtml">Adicionar contração</option>
					</select>
					<span class="translateHtml addTokenHelp"> antes do token de id </span>
					<input class="translatePlaceholder" onkeyup="$('.addTokenButton').val($('.addTokenOptionSelect:selected').text() + $('.addTokenHelp').html() + $(this).val());" name="addTokenId">
					<input type="button" onclick="if ($('[name=addTokenOption]').val() && $('[name=addTokenId]').val()) {{ $('.addTokenForm').submit(); }}" class="translateVal addTokenButton" value="Adicionar token">
					<br><br><i><span class="translateHtml">Dicas:<br>Utilize vírgula para determinar mais de um id de token.<br>Utilize o sinal de maior ">" para indicar intervalo de id (por ex., "4>6" para "de 4 até 6")</span></i>
					{sentid}
					{link}
					{nome}
					{occ}
					{conllu}
					{tokenId}
					{sentnum}
					{textheader}
					{text}
				</form>
			</div>
			<div class="splitSentence tokenization" style="display:none">
				<form action="../cgi-bin/tokenization.py?action=splitSentence" class="splitSentenceForm" method="POST">
					<span class="translateHtml splitSentenceHelp">Separar sentença após o token de id </span>
					<input class="splitSentenceField" onkeyup="$('.splitSentenceButton').val('Separar sentença após o token de id ' + $(this).val());" name="splitSentenceTokenId">
					<br><br><span class="translateHtml splitSentenceHelp">Esta sentença terá seu sent_id modificado?</span>
					<input class="splitSentenceField" style="width:100%" value="{sent_id_plain}" name="sameSentenceId">
					<br><br><span class="translateHtml splitSentenceHelp">A nova sentença receberá qual sent_id?</span>
					<input class="splitSentenceField" style="width:100%" value="{sent_id_plain}-NEW" name="newSentenceId">
					<br><br><span class="translateHtml splitSentenceHelp">Esta sentença terá seu "text" modificado?</span>
					<input class="splitSentenceField" style="width:100%" value="{text_plain}" name="sameText">
					<br><br><span class="translateHtml splitSentenceHelp">A nova sentença receberá qual "text"?</span>
					<input class="splitSentenceField" style="width:100%" value="{text_plain}" name="newText">
					<br><br>
					<input type="button" onclick="if (!anySplitSentenceFieldEmpty()) {{ $('.splitSentenceForm').submit(); }}" class="translateVal splitSentenceButton" value="Separar sentença">
					<br><br>
					{sentid}
					{link}
					{nome}
					{occ}
					{conllu}
					{tokenId}
					{sentnum}
					{textheader}
					{text}
				</form>
			</div>
			<div class="mergeSentences tokenization" style="display:none">
				<form action="../cgi-bin/tokenization.py?action=mergeSentences" class="mergeSentencesForm" method="POST">
					<span class="translateHtml mergeSentencesHelp">Inserir sentença de sent_id </span> 
					<input style="width:250px;" class="translatePlaceholder" onkeyup="$('.mergeSentencesButton').val('Inserir sentença ' + $(this).val() + ' ' + $('.mergeSentencesOptionSelect:selected').text());" name="mergeSentencesId">
					<select name="mergeSentencesOption" onchange="$('.mergeSentencesButton').val('Inserir sentença ' + $('[name=mergeSentencesId]').val() + ' ' + $('.mergeSentencesSelect:selected').text());">
						<option value="right" class="mergeSentencesOptionSelect translateHtml">à direita</option>
						<option value="left" class="mergeSentencesOptionSelect translateHtml">à esquerda</option>
					</select>					
					<input type="button" onclick="if ($('[name=mergeSentencesOption]').val() && $('[name=mergeSentencesId]').val()) {{ $('.mergeSentencesForm').submit(); }}" class="translateVal mergeSentencesButton" value="Inserir sentença">
					<br><br><i><span class="translateHtml">Dica: Utilize vírgula para determinar mais de um sent_id.</span></i>
					{sentid}
					{link}
					{nome}
					{occ}
					{conllu}
					{tokenId}
					{sentnum}
					{textheader}
					{text}
				</form>
			</div>
			<span class="changesNotSaved translateHtml" style="background-color:yellow;"></span>
			</div>'''.format(
				sentid='<input type=hidden name=tokenization_sentid value="' + form['sentid'].value.replace('"', '&quot;') + '">' if 'sentid' in form else '',
				link='<input type=hidden name=tokenization_link_interrogatorio value="' + form['link_interrogatorio'].value + '">' if 'link_interrogatorio' in form and form['link_interrogatorio'].value not in ['teste', 'Busca rápida'] else '',
				nome='<input type=hidden name=tokenization_nome_interrogatorio value="' + form['nome_interrogatorio'].value.replace('"', '&quot;') + '">' if 'nome_interrogatorio' in form and form['nome_interrogatorio'].value not in ['teste', 'Busca rápida'] else '',
				occ='<input type=hidden name=tokenization_occ value="' + form['occ'].value + '">' if 'nome_interrogatorio' in form and form['nome_interrogatorio'].value not in ['teste', 'Busca rápida'] and 'occ' in form else '',
				conllu='<input type=hidden name=tokenization_conllu value="' + ud + '">',
				tokenId='<input type=hidden name=tokenization_tokenId value="' + form['tokenId'].value + '">' if 'tokenId' in form else '',
				sentnum='<input type=hidden name=tokenization_sentnum value="' + str(i) + '">' if 'sentnum' in form else '',
				textheader='<input type=hidden name=tokenization_textheader value="' + form['textheader'].value + '">' if 'textheader' in form else '',
				corpus_plain=ud,
				sent_id_plain=form['sentid'].value,
				text='<input type=hidden name=text value="' + form['text'].value.replace('"', '&quot;') + '">' if 'text' in form else '',
				text_plain=form['text'].value if 'text' in form else '',
			)

			html1 += '<form action="../cgi-bin/inquerito.py?sentnum='+str(i)+'&conllu=' + ud + '&action=alterar" id="dados_inquerito" method="POST">'
			if 'sentid' in form: html1 = html1 + '<input type=hidden name=sentid value="' + form['sentid'].value.replace('"', '\"') + '">'
			if 'link_interrogatorio' in form and form['link_interrogatorio'].value not in ['teste', 'Busca rápida']:
				html1 = html1 + '<input type=hidden name=link_interrogatorio value="' + form['link_interrogatorio'].value + '">'
			if 'nome_interrogatorio' in form and form['nome_interrogatorio'].value not in ['teste', 'Busca rápida']:
				html1 = html1 + '<input type=hidden name=nome_interrogatorio value="' + form['nome_interrogatorio'].value.replace('"', '&quot;') + '">'
				if 'occ' in form: html1 += '<input type=hidden name=occ value="' + form['occ'].value + '">'
			
			if mostrarEtiqueta:
				html1 += '''Tipo de inquérito (etiqueta):<br><br><input type="text" style="border-width: 0px; border-radius: 10px; text-align: center;" placeholder="Crie uma etiqueta para este tipo de inquérito" id=tag name="tag" list="cars" required>'''
				html1 += '<script>var x = document.cookie.split("tag=")[1].split(";")[0]; if (x && x != "NONE") { document.getElementById("tag").value = x }; </script>'
				html1 += '''<datalist id="cars">'''
				if not os.path.isfile('./interrogar-ud/inqueritos_cars.txt'):
					with open('./interrogar-ud/inqueritos_cars.txt', 'w') as f:
						f.write('')
				with open('./interrogar-ud/inqueritos_cars.txt', 'r') as f:
					inqueritos_cars = f.read().splitlines()
				for linha in inqueritos_cars:
					if linha:
						html1 += '<option>' + linha.replace('<', '&lt;').replace('>', '&gt;') + '</option>'
				html1 += "</datalist> "

			html1 += '<br><b class="translateHtml">Edite os valores desejados:</b></div><div class="div01" style="max-width:100%; overflow-x:auto;"><table id="t01">'

			dicionario = dict()
			for a, linha in enumerate(sentence2.splitlines()):
				if '\t' in linha:
					dicionario[linha.split('\t')[0]] = linha

			for a, linha in enumerate(sentence2.splitlines()):
				if not '\t' in linha:
					html1 += f'''<tr><input class="field" value="{linha.replace('<','&lt;').replace('>','&gt;').replace('"', '&quot;')}" type="hidden" name="''' +str(a)+ '''-''' + '''meta"><td style="cursor:pointer; color:black; max-width: 90vw; word-wrap: break-word;" id="''' +str(a)+ '''-''' + '''meta" contenteditable=True class="annotationValue plaintext" colspan="42">''' + web.escape(linha) + '</td></tr>'
				else:
					isBold = "background-color: lightgray;" if 'tokenId' in form and linha.split('\t')[0] in form['tokenId'].value.split(",") else ""
					html1 += f'<tr style="{isBold}">'
					for b, coluna in enumerate(linha.split('\t')):
						drag = 'drag ' if b in [6] else ''
						dragId = 'id ' if b == 0 else ''
						notPipe = "" if b in [1, 2, 4, 5, 9] and coluna != "_" else "notPipe "
						tokenId = f"id_{coluna} " if b == 0 else ""
						html1 += f'''<input class="field" value="{coluna.replace('<','&lt;').replace('>','&gt;').replace('"', '&quot;')}" type=hidden name="''' +str(a)+ '''-''' + str(b) + f'''"><td style="cursor:pointer; color:black;" id="''' +str(a)+ '''-''' + str(b) + f'''" class="{tokenId}{drag}{dragId}{notPipe}annotationValue plaintext" contenteditable=True>''' + web.escape(coluna) + '</td>'
					html1 += '</tr>'

			html1 += '</table>'
			html1 += '</div><input type="hidden" name="textheader" value="' + form['textheader'].value + '"></label><br><br>'
			html1 += '<input type=hidden name=tokenId value="' + form['tokenId'].value + '">' if 'tokenId' in form else ''
			html1 += '</div></form>'
			achou = True
			break
	if not achou: html1 += '<span class="translateHtml">Sentença não encontrada.</span>'

	html = html1 + '''<script>function insertTextAtCursor(text) {
  var sel, range, html;
  if (window.getSelection) {
    sel = window.getSelection();
    if (sel.getRangeAt && sel.rangeCount) {
      range = sel.getRangeAt(0);
      range.deleteContents();
      range.insertNode(document.createTextNode(text));
    }
  } else if (document.selection && document.selection.createRange) {
    document.selection.createRange().text = text;
  }
}


document.querySelector(".plaintext[contenteditable]").addEventListener("paste", function(e) {
  e.preventDefault();
  if (e.clipboardData && e.clipboardData.getData) {
    var text = e.clipboardData.getData("text/plain");
    document.execCommand("insertHTML", false, text);
  } else if (window.clipboardData && window.clipboardData.getData) {
    var text = window.clipboardData.getData("Text");
    insertTextAtCursor(text);
  }
});</script>
''' + html2
	print(html)

elif os.environ['REQUEST_METHOD'] == 'POST' and form['action'].value == 'alterar':
	ud = form['conllu'].value
	if 'nome_interrogatorio' in form: nome = form['nome_interrogatorio'].value
	else: nome = ''
	if 'link_interrogatorio' in form: link = form['link_interrogatorio'].value
	else: link = ''
	if 'sentid' in form: sentid = form['sentid'].value
	else: sentid = ''
	if 'occ' in form: ocorrencias = form['occ'].value
	else: ocorrencias = ''
	text = form['textheader'].value
	tag = form['tag'].value.replace('&lt;','<').replace('&gt;','>').replace(';', '_') if 'tag' in form else 'NONE'
	if tag[0] == '#': tag = tag[1:]
	conlluzao = estrutura_dados.LerUD('./interrogar-ud/conllu/' + ud)
	data = str(datetime.now()).replace(' ','_').split('.')[0]
	inqueritos_concluidos = list()

	sentnum = int(form['sentnum'].value)
	if 'sentid' in form:
		if sentid != [x for x in conlluzao[sentnum] if isinstance(x, str) and x.startswith("# sent_id = ")][0].split("# sent_id = ")[1].split("\n")[0]:
			for i, sentence in enumerate(conlluzao):
				if [x for x in sentence if isinstance(x, str) and x.startswith("# sent_id = ")][0].split("# sent_id = ")[1].split("\n")[0] == sentid:
					sys.stderr.write("\n=== sentnum changed from {} to {}".format(sentnum, i))
					sentnum = i
					break
		else:
			sys.stderr.write("\b=== sentnum did not change")

	for key in dict(form).keys():
		value = dict(form)[key]
		if re.search(r'^\d+-(\d+|meta)$', key) and not '# sent_id = ' in value.value:
			token = int(key.split('-')[0])
			if key.split('-')[1] != 'meta': coluna = int(key.split('-')[1])
			else: coluna = 'meta'
			value = web.unescape(value.value.replace("\n", "").replace("\r", ""))

			#if (coluna == ':' and conlluzao[int(form['sentnum'].value)][token] != value) or (coluna != ':' and conlluzao[int(form['sentnum'].value)][token][coluna] != value):
				#try:
				#print(value)
				#print(conlluzao[int(form['sentnum'].value)][token])
			if coluna != 'meta':
				antes = '\t'.join(conlluzao[sentnum][token])
				conlluzao[sentnum][token][coluna] = value
				depois = '\t'.join(conlluzao[sentnum][token]).replace(value, '<b>' + value + '</b>').replace(conlluzao[sentnum][token][7], conlluzao[sentnum][token][7] + get_head(conlluzao[sentnum], conlluzao[sentnum][token]))
			else:
				antes = conlluzao[sentnum][token]
				conlluzao[sentnum][token] = value
				depois = conlluzao[sentnum][token].replace(value, '<b>' + value + '</b>')
		
			inquerito_concluido = form['textheader'].value + '!@#' + antes + ' --> ' + depois + '!@#' + form['conllu'].value + '!@#' + data
			inquerito_concluido += '!@#' + form['nome_interrogatorio'].value + ' (' + form['occ'].value + ')' if 'occ' in form else '!@#NONE'
			inquerito_concluido += '!@#' + form['link_interrogatorio'].value if 'link_interrogatorio' in form else '!@#NONE'
			inquerito_concluido += '!@#' + tag if 'tag' in form else '!@#NONE'
			inquerito_concluido += '!@#' + form['sentid'].value if 'sentid' in form else '!@#NONE'
			inqueritos_concluidos.append(inquerito_concluido)

	if not os.path.isfile('./interrogar-ud/inqueritos.txt'):
		with open('./interrogar-ud/inqueritos.txt', 'w') as f:
			f.write('')

	with open('./interrogar-ud/inqueritos.txt', 'r') as f:
		inqueritos = f.read()
	with open('./interrogar-ud/inqueritos.txt', 'w') as f:
		f.write("\n".join(inqueritos_concluidos) + '\n' + inqueritos)
	with open('./interrogar-ud/inqueritos_cars.txt', 'r') as f:
		inqueritos_cars = f.read()

	if tag != 'NONE' and not tag in inqueritos_cars:
		with open('./interrogar-ud/inqueritos_cars.txt', 'w') as f:
			f.write(tag + '\n' + inqueritos_cars)
	estrutura_dados.EscreverUD(conlluzao, './interrogar-ud/conllu/' + ud + '_inquerito')
	os.remove('./interrogar-ud/conllu/' + ud)
	os.rename('./interrogar-ud/conllu/' + ud + "_inquerito", './interrogar-ud/conllu/' + ud)

	html = '''<html><head><meta http-equiv="content-type" content="text/html; charset=UTF-8; width=device-width, initial-scale=1.0" name="viewport"></head><body><form action="../cgi-bin/inquerito.py?conllu=''' + ud + '''" method="POST" id="reenviar"><input type=hidden name=sentid value="''' + sentid + '''"><input type=hidden name=occ value="''' + ocorrencias + '''"><input type="hidden" name="textheader" value="''' + text.replace('/BOLD','').replace('@BOLD','').replace('@YELLOW/', '').replace('@PURPLE/', '').replace('@BLUE/', '').replace('@RED/', '').replace('@CYAN/', '').replace('/FONT', '') + '''"><input type=hidden name="nome_interrogatorio" value="''' + nome.replace('"', '&quot;') + '''"><input type=hidden name="link_interrogatorio" value="''' + link + '''"><input type=hidden name=finalizado value=sim>'''
	if 'tag' in form: html += '<input type=hidden name=tag value="' + form['tag'].value + '">'
	html += '<input type=hidden name=tokenId value="' + form['tokenId'].value + '">' if 'tokenId' in form else ''
	html += '''</form><script>document.cookie = "tag=''' + tag.replace('"', '\\"').replace(";", "_") + '''"; document.getElementById('reenviar').submit();</script></body></html>'''
	print(html)

elif 'action' in form and form['action'].value == 'tokenization_log':
	print(printar(coluna=":", tokenization_log=True))

elif 'action' in form and os.environ['REQUEST_METHOD'] == 'POST' and form['action'].value == 'filtrar':
	coluna = form['coluna'].value
	valor = form['valor'].value
	print(printar(coluna, valor, form['onlysent'].value if 'onlysent' in form else False), flush=True)

elif os.environ['REQUEST_METHOD'] != 'POST':
	print(printar())

elif os.environ['REQUEST_METHOD'] == 'POST' and form['action'].value == 'manage_tags':
	print(printar(':', '', False, True))

exit()