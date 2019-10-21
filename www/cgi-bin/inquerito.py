#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print('Content-type:text/html')
print('\n\n')

from functions import corpusGenericoInquerito

mostrarEtiqueta = False
bosqueNaoEncontrado = corpusGenericoInquerito
draggable = [6]

import sys
import cgi, cgitb
cgitb.enable()
import estrutura_dados
import estrutura_ud
import os
from functions import prettyDate, cleanEstruturaUD
from datetime import datetime
import re
from subprocess import call
import html as webpage
import validar_UD

arquivos = list()
for i, arquivo in enumerate(os.listdir('../interrogar-ud/conllu')):
	arquivos.append('<option value="'+arquivo+'">'+arquivo+'</option>')

html = open('../interrogar-ud/inquerito.html', 'r').read()
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

	html1 += '<form name="form_pesquisa" id="form_pesquisa" action="../cgi-bin/inquerito.py?action=filtrar" method="POST"><hr><div id="div_filtro">Filtrar relatório:<br><select name="coluna" id=coluna required><option value=":">Tudo</option><option value="6">Etiqueta</option><option value="0"># text</option><option value="7"># sent_id</option><option value="2">CoNLLU</option><option value="3">Data</option><option value="4">Página no Interrogatório</option></select> <input type=text autofocus="true" name=valor id=valor value="' + valor.replace('"', '&quot;') + '" required> <input name="submit_search" type=submit value="Realizar filtro" style="display:block-inline">'
	if coluna: html1 += ' <a style="display:block-inline" class="close-thik" href="../cgi-bin/inquerito.py"></a>'

	html1 += '<br><br><input type=checkbox name=onlysent checked>Apenas sentenças</input>' if onlysent else '<br><br><input type=checkbox name=onlysent >Apenas sentenças</input>'

	if not "HTTP_HOST" in os.environ: os.environ["HTTP_HOST"] = "localhost:8000"
	html1 += '''</form> - <a href="../interrogar-ud/relatorio.txt" target="_blank">Baixar relatório</a> - <form style="display:inline-block" method="POST" id="managetags_form" action="../cgi-bin/inquerito.py"><input type=hidden name="action" value="manage_tags"><a style="cursor:pointer" onclick="managetags_form.submit()">Gerenciar etiquetas</a></form></div><hr>'''
	relatorio = str(datetime.now()).replace(' ', '_').split('.')[0] + '\nRelatório de Inquéritos - ' + os.environ['HTTP_HOST']
	if coluna: relatorio += '\nFiltro: ' + valor
	relatorio += '\nMostrando apenas as sentenças que foram alteradas' if onlysent else '\nMostrando todas as alterações em todas as sentenças'

	lista_sentences = list()
	relatorio42 = str()

	html1 += '<br><br>'

	if not os.path.isfile('../interrogar-ud/inqueritos.txt'):
		open('../interrogar-ud/inqueritos.txt', 'w').write('')

	html42 = ''
	total = 0
	javistos = list()
	inqueritos = open('../interrogar-ud/inqueritos.txt', 'r').read()
	for a, linha in enumerate(inqueritos.splitlines()):
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
							html42 = html42 + '<p>Página no Interrogatório: <a target="_blank" href="' + linha.split('!@#')[5] + '">' + cgi.escape(linha.split('!@#')[4]).replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<', '&lt;').replace('>', '&gt;').replace('@BOLD', '<b>').replace('/BOLD', '</b>') + '</a></p>'
							relatorio42 += '\n\nPágina no interrogatório: ' + cgi.escape(linha.split('!@#')[4]).replace('<b>', '').replace('</b>', '')
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
					html42 += '''<div class=container><form method="POST" action="../cgi-bin/inquerito.py"><input name="delete_tag" type=hidden value="''' + cgi.escape(linha.split('!@#')[6], quote=True) + '''"><a style="cursor:pointer" onclick="document.getElementsByName('coluna')[0].value = '6'; document.getElementsByName('valor')[0].value = \'''' + cgi.escape(linha.split('!@#')[6], quote=True) + '''\'; document.getElementsByName('form_pesquisa')[0].submit();">#''' + cgi.escape(linha.split('!@#')[6], quote=True) + '''</a> <a style="cursor:pointer" onclick="if (confirmar(\'''' + cgi.escape(linha.split('!@#')[6], quote=True) + '''\') == true) { this.parentNode.submit(); return false; }" class="close-thik"></a></form></div>'''
					total += 1
					javistos.append(linha.split('!@#')[6])


	html = html1 + 'Inquéritos: ' + str(total) + '<br><br>' + html42 + html2
	open('../interrogar-ud/relatorio.txt', 'w').write(relatorio + '\n\n' + 'Inquéritos: ' + str(total) + '\n\nResumo: ' + str(len(lista_sentences)) + ' sentenças alteradas\n' + '\n'.join(lista_sentences) + relatorio42)


if os.environ['REQUEST_METHOD'] == 'POST':
	form = cgi.FieldStorage()
	if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
		html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
		print(html)
		exit()

if os.environ['REQUEST_METHOD'] == "POST" and 'ud' in form.keys() and 'action' in form.keys() and form['action'].value == 'apagarCorpus':
	os.system('rm ../interrogar-ud/conllu/' + form['ud'].value)
	print('<script>window.location = "../cgi-bin/arquivo_ud.cgi"</script>')
	exit()

elif os.environ['REQUEST_METHOD'] == 'POST' and 'delete_tag' in form.keys():
	inqueritos = open('../interrogar-ud/inqueritos.txt', 'r').read()
	tags = open('../interrogar-ud/inqueritos_cars.txt', 'r').read()

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

	with open('../interrogar-ud/inqueritos.txt', 'w') as f:
		f.write('\n'.join(novo_inqueritos))

	with open('../interrogar-ud/inqueritos_cars.txt', 'w') as f:
		f.write('\n'.join(novo_tags))

	html = '<script>window.location = "../cgi-bin/inquerito.py"</script>'


elif os.environ['REQUEST_METHOD'] == 'POST' and 'action' in form.keys() and form['action'].value == 'script':
	inqueritos = open('../interrogar-ud/inqueritos.txt').read().splitlines()

	#pega os headers
	headers = list()
	for linha in open(form['link_interrogatorio'].value, 'r').read().splitlines():
		if '# text =' in linha:
			headers.append(re.sub(r'\<.*?\>', '', linha))

	if form['executar'].value == 'sim':
		with open('../interrogar-ud/scripts/' + estrutura_dados.slugify(form['scriptName'].value), 'wb') as f:
			f.write(form['fileScript'].file.read())

	with open('../interrogar-ud/scripts/headers.txt', 'w') as f:
		f.write("\n".join(headers))
	
	if call('python3 "../interrogar-ud/scripts/MODELO-UD.py" ' + form['conllu'].value + ' ' + form['executar'].value + ' "' + estrutura_dados.slugify(form['scriptName'].value) + '"', shell=True):
		pass
	
	if form['executar'].value == 'exec':
		for linha in open('../interrogar-ud/scripts/novos_inqueritos.txt', 'r').read().splitlines():
			if form['nome_interrogatorio'] not in ['teste', 'Busca rápida']:
				inqueritos.insert(0, linha.rsplit('!@#', 1)[0] + '!@#' + form['nome_interrogatorio'].value + ' (' + form['occ'].value + ')!@#' + form['link_interrogatorio'].value + '!@#' + form['scriptName'].value + '!@#' + linha.rsplit('!@#', 1)[1])
			else:
				inqueritos.insert(0, linha.rsplit('!@#', 1)[0] + '!@#NONE!@#NONE!@#' + form['scriptName'].value + '!@#' + linha.rsplit('!@#', 1)[1])

		cars = open('../interrogar-ud/inqueritos_cars.txt', 'r').read().splitlines()
		if not form['scriptName'].value in cars:
			with open('../interrogar-ud/inqueritos_cars.txt', 'w') as f:
				f.write(form['scriptName'].value + '\n' + "\n".join(cars))

		open('../interrogar-ud/inqueritos.txt', 'w').write('\n'.join(inqueritos))
		html = '''<form id="submeter" action="../cgi-bin/inquerito.py?action=filtrar" method="POST"><input type=hidden name=coluna value=6><input type=hidden name=valor value="''' + form['scriptName'].value.replace('"', '&quot;') + '"></form>'
		html += '<script>document.getElementById("submeter").submit();</script>'

		os.remove('../interrogar-ud/conllu/' + form['conllu'].value)
		os.rename('../interrogar-ud/conllu/' + form['conllu'].value + '_script', '../interrogar-ud/conllu/' + form['conllu'].value)
		os.remove('../interrogar-ud/scripts/novos_inqueritos.txt')
			
	elif form['executar'].value == 'sim':
		try:
			with open('../interrogar-ud/scripts/sim.txt', 'r') as f:
				sim = f.read()
		except:
			with open("../cgi-bin/error.log", "r") as f:
				print(f.read().splitlines()[-1])
				exit()
		html = f'<title>Simulação de correção em lote</title><h1>Simulação ({round(len(sim.splitlines())/4)})</h1>Verifique se as alterações estão adequadas e execute o script de correção no <a style="color:blue; cursor:pointer;" onclick="window.scrollTo(0,document.body.scrollHeight);">final da página</a>.\
		<br>Nome da correção: ' + form['scriptName'].value + '\
		<br>Corpus: <a target="_blank" href="../interrogar-ud/conllu/' + form['conllu'].value + '" download>' + form['conllu'].value + '</a>\
		<hr>'
		html += '<pre>' + sim.replace('<', '&lt;').replace('>', '&gt;')
		html += '</pre>'
		html += '<br><form action="../cgi-bin/inquerito.py?action=script&executar=exec" method="POST"><input type=hidden name="nome_interrogatorio" value="''' + form['nome_interrogatorio'].value + '''"><input type=hidden name=occ value="''' + form['occ'].value + '''"><input type=hidden name="link_interrogatorio" value="''' + form['link_interrogatorio'].value + '''"><input type=hidden name="conllu" value="''' + form['conllu'].value + '''"><input type=hidden value="''' + form['scriptName'].value.replace('"', '&quot;') + '''" name="scriptName"><input type=submit value="Executar script"></form>'''
		os.remove('../interrogar-ud/scripts/sim.txt')

	os.remove('../interrogar-ud/scripts/headers.txt')

elif os.environ['REQUEST_METHOD'] == 'POST' and (not 'action' in form.keys() or (form['action'].value != 'alterar' and form['action'].value != 'filtrar' and form['action'].value != 'script' and form['action'].value != 'manage_tags')):
	html1 = html1.replace('<title>Sistema de inquéritos</title>', '<title>Novo inquérito: Interrogatório</title>') if not 'finalizado' in form else html1.replace('<title>Sistema de inquéritos</title>', '<title>Inquérito realizado com sucesso: Interrogatório</title>')
	ud = form['conllu'].value
	colored_ud = ud
	if not os.path.isfile('../interrogar-ud/conllu/' + ud):
		colored_ud = '<span style="background-color:red; color:white;">"' + ud + '" não encontrado</span>'
		ud = bosqueNaoEncontrado
	conlluzao = estrutura_dados.LerUD('../interrogar-ud/conllu/' + ud)
	if 'finalizado' in form:
		erros = []
		if 'sentid' in form:
			erros = validar_UD.validate('../interrogar-ud/conllu/' + ud, sent_id=form['sentid'].value, noMissingToken=True)
		alertColor = "cyan" if not erros else "yellow"
		alertBut = "" if not erros else ", mas atenção:"
		html1 += f'<span style="background-color: {alertColor}">Alteração realizada com sucesso{alertBut}</span>'
		if alertBut:
			html1 += "<ul>" 
			for erro in erros:
				html1 += f'<li>{erro}</li><ul>'
				for sentence in erros[erro]:
					if sentence and sentence['sentence']:
						html1 += f'''<li><a style="cursor:pointer" onclick="$('.id_{cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].id)}').focus();">{cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].id)} / {cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].word)}{' / ' + cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].col[sentence['attribute']]) if sentence['attribute'] else ""}</a></li>'''
				html1 += "</ul>"
			html1 += "</ul>"
		html1 += '<br>'

	html1 = html1.split('<div class="header">')[0] + '<div class="header"><h1>Novo inquérito</h1><br><br>' + colored_ud + '<br><br><a href="../cgi-bin/inquerito.py">Relatório de inquéritos</a> - <form style="display:inline-block" target="_blank" method="POST" action="../cgi-bin/draw_tree.py?conllu=' + ud + '"><a href="#" onclick="this.parentNode.submit()">Visualizar árvore</a><input type=hidden name=text value="' + form['textheader'].value + '"><input type=hidden name=sent_id value="' + form['sentid'].value + '"></form> - <a style="cursor:pointer;" onclick="window.close()" class="endInquerito">Encerrar inquérito</a></div>' + html1.split('</div>', 3)[3]

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
				if not os.path.isfile('../interrogar-ud/inqueritos_cars.txt'): open('../interrogar-ud/inqueritos_cars.txt', 'w').write('')
				for linha in open('../interrogar-ud/inqueritos_cars.txt', 'r').read().splitlines():
					if linha:
						html1 += '<option>' + linha.replace('<','&lt;').replace('>','&gt;') + '</option>'
				html1 += "</datalist> "
			html1 += '<h3>Controles:</h3>Esc: Encerrar inquérito<br>Tab / Shift + Tab: ir para coluna à direita/esquerda<br>↑ / ↓: ir para linha acima/abaixo<br>↖: Arraste a coluna <b>dephead</b> de um token para a linha do token do qual ele depende<br>Shift + Scroll: Mover tabela para os lados<br><br>'
			html1 += '<input style="display: inline-block; margin: 0px;" type="button" onclick="enviar()" class="btn-gradient blue small" id="sendAnnotation" value="Realizar alteração (Ctrl+Enter)"><!--br><br><br-->'
			html1 += '<br><br><br><b>Edite as colunas desejadas:</b></div><div class="div01" style="max-width:100%; overflow-x:auto;"><table id="t01">'

			dicionario = dict()
			for a, linha in enumerate(sentence2.splitlines()):
				if '\t' in linha:
					dicionario[linha.split('\t')[0]] = linha

			for a, linha in enumerate(sentence2.splitlines()):
				if not '\t' in linha:
					html1 += f'''<tr><input class="field" value="{linha.replace('<','&lt;').replace('>','&gt;').replace('"', '&quot;')}" type="hidden" name="''' +str(a)+ '''-''' + '''meta"><td style="cursor:pointer; color:black; max-width: 90vw; word-wrap: break-word;" id="''' +str(a)+ '''-''' + '''meta" contenteditable=True class="annotationValue plaintext" colspan="42">''' + linha + '</td></tr>'
				else:
					isBold = "background-color: lightgray;" if 'tokenId' in form and linha.split('\t')[0] == form['tokenId'].value else ""
					html1 += f'<tr style="{isBold}">'
					for b, coluna in enumerate(linha.split('\t')):
						drag = 'drag ' if b in draggable else ''
						dragId = 'id ' if b == 0 else ''
						notPipe = "" if b in [4, 5, 9] and coluna != "_" else "notPipe "
						tokenId = f"id_{coluna} " if b == 0 else ""
						html1 += f'''<input class="field" value="{coluna.replace('<','&lt;').replace('>','&gt;').replace('"', '&quot;')}" type=hidden name="''' +str(a)+ '''-''' + str(b) + f'''"><td style="cursor:pointer; color:black;" id="''' +str(a)+ '''-''' + str(b) + f'''" class="{tokenId}{drag}{dragId}{notPipe}annotationValue plaintext" contenteditable=True>''' + coluna.replace('<','&lt;').replace('>','&gt;') + '</td>'
					html1 += '</tr>'

			html1 += '</table></div><input type="hidden" name="textheader" value="' + form['textheader'].value + '"></label><br><br>'
			html1 += '<input type=hidden name=tokenId value="' + form['tokenId'].value + '">' if 'tokenId' in form else ''
			html1 += '</div></form>'
			achou = True
			break
	if not achou: html1 += 'Sentença não encontrada.'

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
	conlluzao = estrutura_dados.LerUD('../interrogar-ud/conllu/' + ud)
	data = str(datetime.now()).replace(' ','_').split('.')[0]
	inqueritos_concluidos = list()

	for key in dict(form).keys():
		value = dict(form)[key]
		if re.search(r'^\d+-(\d+|meta)$', key):
			token = int(key.split('-')[0])
			if key.split('-')[1] != 'meta': coluna = int(key.split('-')[1])
			else: coluna = 'meta'
			value = webpage.unescape(value.value)

			#if (coluna == ':' and conlluzao[int(form['sentnum'].value)][token] != value) or (coluna != ':' and conlluzao[int(form['sentnum'].value)][token][coluna] != value):
				#try:
				#print(value)
				#print(conlluzao[int(form['sentnum'].value)][token])
			if coluna != 'meta':
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

	if not os.path.isfile('../interrogar-ud/inqueritos.txt'):
		open('../interrogar-ud/inqueritos.txt', 'w').write('')

	inqueritos = open('../interrogar-ud/inqueritos.txt', 'r').read()
	open('../interrogar-ud/inqueritos.txt', 'w').write("\n".join(inqueritos_concluidos) + '\n' + inqueritos)
	inqueritos_cars = open('../interrogar-ud/inqueritos_cars.txt', 'r').read()

	if tag != 'NONE' and not tag in inqueritos_cars: open('../interrogar-ud/inqueritos_cars.txt', 'w').write(tag + '\n' + inqueritos_cars)
	estrutura_dados.EscreverUD(conlluzao, '../interrogar-ud/conllu/' + ud)

	html = '''<html><head><meta http-equiv="content-type" content="text/html; charset=UTF-8; width=device-width, initial-scale=1.0" name="viewport"></head><body><form action="../cgi-bin/inquerito.py?conllu=''' + ud + '''" method="POST" id="reenviar"><input type=hidden name=sentid value="''' + sentid + '''"><input type=hidden name=occ value="''' + ocorrencias + '''"><input type="hidden" name="textheader" value="''' + text.replace('/BOLD','').replace('@BOLD','').replace('@YELLOW/', '').replace('@PURPLE/', '').replace('@BLUE/', '').replace('@RED/', '').replace('@CYAN/', '').replace('/FONT', '') + '''"><input type=hidden name="nome_interrogatorio" value="''' + nome + '''"><input type=hidden name="link_interrogatorio" value="''' + link + '''"><input type=hidden name=finalizado value=sim>'''
	if 'tag' in form: html += '<input type=hidden name=tag value="' + form['tag'].value + '">'
	html += '<input type=hidden name=tokenId value="' + form['tokenId'].value + '">' if 'tokenId' in form else ''
	html += '''</form><script>document.cookie = "tag=''' + tag.replace('"', '\\"').replace(";", "_") + '''"; document.getElementById('reenviar').submit();</script></body></html>'''

elif os.environ['REQUEST_METHOD'] != 'POST':
	printar()

elif os.environ['REQUEST_METHOD'] == 'POST' and form['action'].value == 'filtrar':
	coluna = form['coluna'].value
	valor = form['valor'].value
	printar(coluna, valor, form['onlysent'].value if 'onlysent' in form else False)

elif os.environ['REQUEST_METHOD'] == 'POST' and form['action'].value == 'manage_tags':
	printar(':', '', False, True)

print(html)
