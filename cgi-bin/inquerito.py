#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print('Content-type:text/html')
print('\n\n')

import sys
import cgi, cgitb
cgitb.enable()
import estrutura_dados
import estrutura_ud
import os
from datetime import datetime
import re
from subprocess import call
import html as webpage

#import json

#with open('/interrogar-ud/cookies.json', 'w') as fp:
	#json.dump(dict(os.environ), fp)

arquivos = list()
for i, arquivo in enumerate(os.listdir('/interrogar-ud/conllu')):
	arquivos.append('<option value="'+arquivo+'">'+arquivo+'</option>')

html = open('/interrogar-ud/inquerito.html', 'r').read()
html = html.split('<select name="conllu">')[0] + '<select name="conllu">' + "\n".join(arquivos) + '</select>' + html.split('</select>')[1]

html1 = html.split('<!--SPLIT-->')[0]
html2 = html.split('<!--SPLIT-->')[1]

def get_head(frase, token):
	for linha in frase:
		if isinstance(linha, list) and token[6] == linha[0]:
			return ' (' + linha[1] + ')'
	return ''

def printar(coluna='', valor='', onlysent=False, managetags=False):
	global html
	global html1
	global html2
	if valor and valor[0] == '#': valor = ''.join(valor[1:])

	html1 = html1.replace('<title>Sistema de inquéritos</title>', '<title>Relatório de inquéritos: Interrogatório</title>')

	html1 += '<form name="form_pesquisa" id="form_pesquisa" action="/cgi-bin/inquerito.py?action=filtrar" method="POST"><hr><div id="div_filtro">Filtrar relatório:<br><select name="coluna" id=coluna required><option value=":">Tudo</option><option value="6">Etiqueta</option><option value="0"># text</option><option value="7"># sent_id</option><option value="2">CoNLLU</option><option value="3">Data</option><option value="4">Página no Interrogatório</option></select> <input type=text autofocus="true" name=valor id=valor value="' + valor.replace('"', '&quot;') + '" required> <input name="submit_search" type=submit value="Realizar filtro" style="display:block-inline">'
	if coluna: html1 += ' <a style="display:block-inline" class="close-thik" href="/cgi-bin/inquerito.py"></a>'

	html1 += '<br><br><input type=checkbox name=onlysent checked>Apenas sentenças</input>' if onlysent else '<br><br><input type=checkbox name=onlysent >Apenas sentenças</input>'

	html1 += '''</form> - <a href="/interrogar-ud/relatorio.txt" target="_blank">Baixar relatório</a> - <form style="display:inline-block" method="POST" id="managetags_form" action="/cgi-bin/inquerito.py"><input type=hidden name="action" value="manage_tags"><a style="cursor:pointer" onclick="managetags_form.submit()">Gerenciar etiquetas</a></form></div><hr>'''
	relatorio = str(datetime.now()).replace(' ', '_').split('.')[0] + '\nRelatório de Inquéritos - ' + os.environ['HTTP_HOST']
	if coluna: relatorio += '\nFiltro: ' + valor
	relatorio += '\nMostrando apenas as sentenças que foram alteradas' if onlysent else '\nMostrando todas as alterações em todas as sentenças'

	lista_sentences = list()
	relatorio42 = str()

	html1 += '<br><br>'

	if not os.path.isfile('/interrogar-ud/inqueritos.txt'):
		open('/interrogar-ud/inqueritos.txt', 'w').write('')

	html42 = ''
	total = 0
	javistos = list()
	inqueritos = open('/interrogar-ud/inqueritos.txt', 'r').read()
	for a, linha in enumerate(inqueritos.splitlines()):
		if linha.strip() != '':
			if not managetags:
				if (coluna != ':' and valor and len(linha.split('!@#')) > int(coluna) and (re.search(valor, linha.split('!@#')[int(coluna)], flags=re.I|re.M)) and linha.split('!@#')[int(coluna)] != 'NONE') or (not coluna) or (coluna == ':' and re.search(valor, linha, flags=re.I|re.M)):
					if (not onlysent) or (onlysent and not linha.split('!@#')[0] in javistos):
						html42 += '<div class="container"><form target="_blank" id="form_' + str(a) + '" action="/cgi-bin/inquerito.py" method="POST"><input name="textheader" type="hidden" value="' + linha.split('!@#')[0] + '"><input name="conllu" type="hidden" value="' + linha.split('!@#')[2] + '">'
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
							html42 = html42 + '<p>Página no Interrogatório: <a target="_blank" href="' + linha.split('!@#')[5] + '">' + linha.split('!@#')[4].replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<', '&lt;').replace('>', '&gt;').replace('@BOLD', '<b>').replace('/BOLD', '</b>') + '</a></p>'
							relatorio42 += '\n\nPágina no interrogatório: ' + linha.split('!@#')[4].replace('<b>', '').replace('</b>', '')
						if not onlysent:
							html42 += '<pre>ANTES:\t' + linha.split('!@#')[1].split(' --> ')[0].replace('<b>', '@BOLD').replace('</b>','/BOLD').replace('<','&lt;').replace('>','&gt;').replace('@BOLD', '<b>').replace('/BOLD', '</b>') + '</pre><pre>DEPOIS:\t' + linha.split('!@#')[1].split(' --> ')[1].replace('<b>','@BOLD').replace('</b>','/BOLD').replace('<','&lt;').replace('>','&gt;').replace('@BOLD', '<b>').replace('/BOLD', '</b>') + '</pre>'
							relatorio42 += '\n\nANTES:\t' + linha.split('!@#')[1].split(' --> ')[0].replace('<b>', '').replace('</b>','') + '\nDEPOIS:\t' + linha.split('!@#')[1].split(' --> ')[1].replace('<b>','').replace('</b>','')
						html42 += '<small><p><a href="#" onclick="document.getElementById(\'coluna\').value=\'2\'; document.getElementById(\'valor\').value=\'' + linha.split('!@#')[2] + '\'; document.getElementById(\'form_pesquisa\').submit();">' + linha.split('!@#')[2] + '</a></p><p>' + linha.split('!@#')[3] + '</p></small></form></div>'
						relatorio42 += '\n\n' + linha.split('!@#')[2]
						relatorio42 += '\n' + linha.split('!@#')[3]
						total += 1
						javistos.append(linha.split('!@#')[0])
			
			elif managetags:
				if len(linha.split('!@#')) >= 7 and not linha.split('!@#')[6] in javistos and linha.split('!@#')[6] != 'NONE':
					html42 += '''<div class=container><form method="POST" action="/cgi-bin/inquerito.py"><input name="delete_tag" type=hidden value="''' + cgi.escape(linha.split('!@#')[6], quote=True) + '''"><a style="cursor:pointer" onclick="document.getElementsByName('coluna')[0].value = '6'; document.getElementsByName('valor')[0].value = \'''' + cgi.escape(linha.split('!@#')[6], quote=True) + '''\'; document.getElementsByName('form_pesquisa')[0].submit();">#''' + cgi.escape(linha.split('!@#')[6], quote=True) + '''</a> <a style="cursor:pointer" onclick="if (confirmar(\'''' + cgi.escape(linha.split('!@#')[6], quote=True) + '''\') == true) { this.parentNode.submit(); return false; }" class="close-thik"></a></form></div>'''
					total += 1
					javistos.append(linha.split('!@#')[6])


	html = html1 + 'Inquéritos: ' + str(total) + '<br><br>' + html42 + html2
	open('/interrogar-ud/relatorio.txt', 'w').write(relatorio + '\n\n' + 'Inquéritos: ' + str(total) + '\n\nResumo: ' + str(len(lista_sentences)) + ' sentenças alteradas\n' + '\n'.join(lista_sentences) + relatorio42)


if os.environ['REQUEST_METHOD'] == 'POST':
	form = cgi.FieldStorage()
	if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
		html = '<script>window.location = "/interrogar-ud/autenticar.html"</script>'
		print(html)
		exit()

if os.environ['REQUEST_METHOD'] == 'POST' and 'delete_tag' in form.keys():
	inqueritos = open('/interrogar-ud/inqueritos.txt', 'r').read()
	tags = open('/interrogar-ud/inqueritos_cars.txt', 'r').read()

	novo_inqueritos = list()
	for inquerito in inqueritos.splitlines():
		if len(inquerito.split('!@#')) >= 7 and inquerito.split('!@#')[6] == webpage.unescape(form['delete_tag'].value):
			continue
		else:
			novo_inqueritos.append(inquerito)

	novo_tags = list()
	for tag in tags.splitlines():
		if tag == webpage.unescape(form['delete_tag'].value):
			continue
		else:
			novo_tags.append(tag)

	with open('/interrogar-ud/inqueritos.txt', 'w') as f:
		f.write('\n'.join(novo_inqueritos))

	with open('/interrogar-ud/inqueritos_cars.txt', 'w') as f:
		f.write('\n'.join(novo_tags))

	html = '<script>window.location = "/cgi-bin/inquerito.py"</script>'


elif os.environ['REQUEST_METHOD'] == 'POST' and 'action' in form.keys() and form['action'].value == 'script':
	inqueritos = open('/interrogar-ud/inqueritos.txt').read().splitlines()

	#pega os headers
	headers = list()
	for linha in open(form['link_interrogatorio'].value, 'r').read().splitlines():
		if '# text = ' in linha:
			headers.append(re.sub(r'\<.*?\>', '', linha))

	open('/interrogar-ud/scripts/headers.txt', 'w').write("\n".join(headers))
	call('python3 "/interrogar-ud/scripts/MODELO-UD.py" ' + form['conllu'].value + ' ' + form['executar'].value + ' "' + form['script'].value + '"', shell=True)

	if form['executar'].value == 'exec':
		for linha in open('/interrogar-ud/scripts/novos_inqueritos.txt', 'r').read().splitlines():
			if form['nome_interrogatorio'].value != 'teste':
				inqueritos.insert(0, linha.rsplit('!@#', 1)[0] + '!@#' + form['nome_interrogatorio'].value + ' (' + form['occ'].value + ')!@#' + form['link_interrogatorio'].value + '!@#' + form['script'].value + '!@#' + linha.rsplit('!@#', 1)[1])
			else:
				inqueritos.insert(0, linha.rsplit('!@#', 1)[0] + '!@#NONE!@#NONE!@#' + form['script'].value + '!@#' + linha.rsplit('!@#', 1)[1])

		cars = open('/interrogar-ud/inqueritos_cars.txt', 'r').read().splitlines()
		if not form['script'].value in cars:
			with open('/interrogar-ud/inqueritos_cars.txt', 'w') as f:
				f.write(form['script'].value + '\n' + "\n".join(cars))

		open('/interrogar-ud/inqueritos.txt', 'w').write('\n'.join(inqueritos))
		html = '''<form id="submeter" action="/cgi-bin/inquerito.py?action=filtrar" method="POST"><input type=hidden name=coluna value=6><input type=hidden name=valor value="''' + form['script'].value + '"></form>'
		html += '<script>document.getElementById("submeter").submit();</script>'

		os.remove('/interrogar-ud/conllu/' + form['conllu'].value)
		os.rename('/interrogar-ud/conllu/' + form['conllu'].value + '_script', '/interrogar-ud/conllu/' + form['conllu'].value)
		os.remove('/interrogar-ud/scripts/novos_inqueritos.txt')
			
	elif form['executar'].value == 'sim':
		html = 'Simulação:'
		html += '<pre>' + open('/interrogar-ud/scripts/sim.txt', 'r').read().replace('<', '&lt;').replace('>','&gt;')
		html += '</pre>'
		html += '<br><form action="/cgi-bin/inquerito.py?action=script&executar=exec" method="POST"><input type=hidden name="nome_interrogatorio" value="''' + form['nome_interrogatorio'].value + '''"><input type=hidden name=occ value="''' + form['occ'].value + '''"><input type=hidden name="link_interrogatorio" value="''' + form['link_interrogatorio'].value + '''"><input type=hidden name="conllu" value="''' + form['conllu'].value + '''"><input type=hidden value="''' + form['script'].value + '''" name="script"><input type=submit value="Executar script"></form>'''
		os.remove('/interrogar-ud/scripts/sim.txt')

	os.remove('/interrogar-ud/scripts/headers.txt')

elif os.environ['REQUEST_METHOD'] == 'POST' and (not 'action' in form.keys() or (form['action'].value != 'alterar' and form['action'].value != 'filtrar' and form['action'].value != 'script' and form['action'].value != 'manage_tags')):
	html1 = html1.replace('<title>Sistema de inquéritos</title>', '<title>Novo inquérito: Interrogatório</title>')
	ud = form['conllu'].value
	colored_ud = ud
	if not os.path.isfile('/interrogar-ud/conllu/' + ud):
		colored_ud = '<span style="background-color:red; color:white;">"' + ud + '" não encontrado</span>'
		ud = 'bosque_UD_2.4.conllu'
	conlluzao = estrutura_dados.LerUD('/interrogar-ud/conllu/' + ud)
	if 'finalizado' in form: html1 += '<span style="background-color: cyan">Alteração realizada com sucesso!</span><br><br><br>'

	html1 = html1.split('<div class="header">')[0] + '<div class="header"><h1>Novo inquérito</h1><br><br>' + colored_ud + '<br><br><a href="inquerito.py">Relatório de inquéritos</a> - <form style="display:inline-block" target="_blank" method="POST" action="/cgi-bin/draw_tree.py?conllu=' + ud + '"><a href="#" onclick="this.parentNode.submit()">Visualizar árvore</a><input type=hidden name=text value="' + form['textheader'].value + '"><input type=hidden name=sent_id value="' + form['sentid'].value + '"></form> - <a href="javascript:window.close()">Encerrar inquérito</a></div>' + html1.split('</div>', 2)[2]

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
			html1 += '<form action="/cgi-bin/inquerito.py?sentnum='+str(i)+'&conllu=' + ud + '&action=alterar" id="dados_inquerito" method="POST">'
			if 'sentid' in form: html1 = html1 + '<input type=hidden name=sentid value="' + form['sentid'].value.replace('"', '\"') + '">'
			if 'link_interrogatorio' in form and 'teste' != form['link_interrogatorio'].value:
				html1 = html1 + '<input type=hidden name=link_interrogatorio value="' + form['link_interrogatorio'].value + '">'
			if 'nome_interrogatorio' in form and 'teste' != form['nome_interrogatorio'].value:
				html1 = html1 + '<input type=hidden name=nome_interrogatorio value="' + form['nome_interrogatorio'].value.replace('"', '&quot;') + '">'
				if 'occ' in form: html1 += '<input type=hidden name=occ value="' + form['occ'].value + '">'
			html1 += '''Tipo de inquérito:<br><br><input type="text" style="border-width: 0px; border-radius: 10px; text-align: center;" placeholder="Crie uma etiqueta para este tipo de inquérito" id=tag name="tag" list="cars" required>'''
			html1 += '<script>var x = document.cookie.split("tag=")[1]; if (x && x != "NONE") { document.getElementById("tag").value = x }; </script>'
			html1 += '''<datalist id="cars">'''
			if not os.path.isfile('/interrogar-ud/inqueritos_cars.txt'): open('/interrogar-ud/inqueritos_cars.txt', 'w').write('')
			for linha in open('/interrogar-ud/inqueritos_cars.txt', 'r').read().splitlines():
				if linha:
					html1 += '<option>' + linha.replace('<','&lt;').replace('>','&gt;') + '</option>'
			html1 += '</datalist> <input style="display: inline-block;" type="button" onclick="enviar()" value="Realizar alteração"><!--br><br><br-->'
			html1 += '<br><br><br><b>Edite as colunas desejadas:</b></div><table id="t01">'

			dicionario = dict()
			for a, linha in enumerate(sentence2.splitlines()):
				if '\t' in linha:
					dicionario[linha.split('\t')[0]] = linha

			for a, linha in enumerate(sentence2.splitlines()):
				if not '\t' in linha:
					html1 += '''<tr><input class="field" type="hidden" name="''' +str(a)+ '''-''' + ''':"><td id="''' +str(a)+ '''-''' + ''':" contenteditable=True colspan="42" style="cursor:pointer; color:black;">''' + linha + '</td></tr>'
				else:
					html1 += '<tr>'
					for b, coluna in enumerate(linha.split('\t')):
						#if b == 6 and re.search(r'^\d+$', coluna) and coluna in dicionario.keys():
							#html1 += '''<input class="field" type=hidden name="''' +str(a)+ '''-''' + str(b) + '''"><td id="''' +str(a)+ '''-''' + str(b) + '''" contenteditable=True style="cursor:pointer; color:black;" onclick="this.Focus(); this.Select();"><div class="tooltip">''' + coluna.replace('<','&lt;').replace('>','&gt;') + '<span class="tooltiptextfix">' + dicionario[coluna].split('\t', 1)[1].replace('<','&lt;').replace('>','&gt;') + '</span></div></td>'
						#else:
						html1 += '''<input class="field" type=hidden name="''' +str(a)+ '''-''' + str(b) + '''"><td id="''' +str(a)+ '''-''' + str(b) + '''" contenteditable=True style="cursor:pointer; color:black;">''' + coluna.replace('<','&lt;').replace('>','&gt;') + '</td>'
					html1 += '</tr>'

			html1 += '</table><input type="hidden" name="textheader" value="' + form['textheader'].value + '"></label><br><br>'
			html1 += '</div></form>'
			achou = True
			break
	if not achou: html1 += 'Sentença não encontrada.'

	html = html1 + html2

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
	conlluzao = estrutura_dados.LerUD('/interrogar-ud/conllu/' + ud)	
	data = str(datetime.now()).replace(' ','_').split('.')[0]
	inqueritos_concluidos = list()

	for key in dict(form).keys():
		value = dict(form)[key]
		if re.search(r'^\d+-(\d+|:)$', key):
			token = int(key.split('-')[0])
			if key.split('-')[1] != ':': coluna = int(key.split('-')[1])
			else: coluna = ':'
			value = webpage.unescape(value.value)

			if (coluna == ':' and conlluzao[int(form['sentnum'].value)][token] != value) or (coluna != ':' and conlluzao[int(form['sentnum'].value)][token][coluna] != value):
				#try:
				#print(value)
				#print(conlluzao[int(form['sentnum'].value)][token])
				if coluna != ':':
					antes = '\t'.join(conlluzao[int(form['sentnum'].value)][token])
					conlluzao[int(form['sentnum'].value)][token][coluna] = value
					depois = '\t'.join(conlluzao[int(form['sentnum'].value)][token]).replace(value, '<b>' + value + '</b>').replace(conlluzao[int(form['sentnum'].value)][token][7], conlluzao[int(form['sentnum'].value)][token][7] + get_head(conlluzao[int(form['sentnum'].value)], conlluzao[int(form['sentnum'].value)][token]))
				else:
					antes = conlluzao[int(form['sentnum'].value)][token]
					conlluzao[int(form['sentnum'].value)][token] = value
					depois = conlluzao[int(form['sentnum'].value)][token].replace(value, '<b>' + value + '</b>')
			
				inquerito_concluido = form['textheader'].value + '!@#' + antes + ' --> ' + depois + '!@#' + form['conllu'].value + '!@#' + data
				inquerito_concluido += '!@#' + form['nome_interrogatorio'].value + ' (' + form['occ'].value + ')' if 'occ' in form else '!@#NONE'
				inquerito_concluido += '!@#' + form['link_interrogatorio'].value if 'link_interrogatorio' in form else '!@#NONE'
				inquerito_concluido += '!@#' + tag if 'tag' in form else '!@#NONE'
				inquerito_concluido += '!@#' + form['sentid'].value if 'sentid' in form else '!@#NONE'
				inqueritos_concluidos.append(inquerito_concluido)

	if not os.path.isfile('/interrogar-ud/inqueritos.txt'):
		open('/interrogar-ud/inqueritos.txt', 'w').write('')

	inqueritos = open('/interrogar-ud/inqueritos.txt', 'r').read()
	open('/interrogar-ud/inqueritos.txt', 'w').write("\n".join(inqueritos_concluidos) + '\n' + inqueritos)
	inqueritos_cars = open('/interrogar-ud/inqueritos_cars.txt', 'r').read()

	if tag != 'NONE' and not tag in inqueritos_cars: open('/interrogar-ud/inqueritos_cars.txt', 'w').write(tag + '\n' + inqueritos_cars)
	estrutura_dados.EscreverUD(conlluzao, '/interrogar-ud/conllu/' + ud)

	html = '''<html><head><meta http-equiv="content-type" content="text/html; charset=UTF-8; width=device-width, initial-scale=1.0" name="viewport"></head><body><form action="/cgi-bin/inquerito.py?conllu=''' + ud + '''" method="POST" id="reenviar"><input type=hidden name=sentid value="''' + sentid + '''"><input type=hidden name=occ value="''' + ocorrencias + '''"><input type="hidden" name="textheader" value="''' + text.replace('/BOLD','').replace('@BOLD','').replace('@YELLOW/', '').replace('@PURPLE/', '').replace('@BLUE/', '').replace('@RED/', '').replace('@CYAN/', '').replace('/FONT', '') + '''"><input type=hidden name="nome_interrogatorio" value="''' + nome + '''"><input type=hidden name="link_interrogatorio" value="''' + link + '''"><input type=hidden name=finalizado value=sim>'''
	if 'tag' in form: html += '<input type=hidden name=tag value="' + form['tag'].value + '">'
	html += '''</form><script>document.cookie = "tag=''' + tag.replace('"', '\\"') + '''"; document.getElementById('reenviar').submit();</script></body></html>'''

elif os.environ['REQUEST_METHOD'] != 'POST':
	printar()

elif os.environ['REQUEST_METHOD'] == 'POST' and form['action'].value == 'filtrar':
	coluna = form['coluna'].value
	valor = form['valor'].value
	printar(coluna, valor, form['onlysent'].value if 'onlysent' in form else False)

elif os.environ['REQUEST_METHOD'] == 'POST' and form['action'].value == 'manage_tags':
	printar(':', '', False, True)

print(html)
