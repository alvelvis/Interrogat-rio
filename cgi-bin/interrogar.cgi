#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import os
import cgi,cgitb
cgitb.enable()
import re
import estrutura_dados
from estrutura_dados import slugify as slugify
import interrogar_UD
from datetime import datetime
import functions
from functions import tabela

#if not 'REQUEST_METHOD' in os.environ:
#	os.environ['REQUEST_METHOD'] = 'POST'

#GET
if os.environ['REQUEST_METHOD'] != "POST":

	arquivos = list()
	for i, arquivo in enumerate(os.listdir('/interrogar-ud/conllu')):
		arquivos.append('<option value ="'+arquivo+'">'+arquivo+'</option>')
	html = open('/interrogar-ud/interrogar_UDnew.html', 'r').read()
	html1 = html.split('<!--SPLIT-->')[0]
	html2 = html.split('<!--SPLIT-->')[1]

	criterios = open('/interrogar-ud/criterios.txt', 'r').read().split('!@#')
	#html1 += '<h3><a style="color:black" id="topo">Critérios de busca:</a></h3><hr>'
	#for i, criterio in enumerate(criterios[1:]):
	#	html1 += '<a href="#criterio_' + str(i+1) + '">' + criterio.splitlines()[0].replace('h3','h4') + '</a>'

	for i, criterio in enumerate(criterios[1:]):
		html1 += '<a id="criterio_' + str(i+1) + '"></a><div class="container-lr">' + criterio
		#html1 += '<p><a href="#topo">[Voltar ao topo]</a></p>'
		html1 += '</div>\n'
	html = html1 + html2

	print(html.split('<select name="conllu">')[0] + '<select name="conllu">' + "\n".join(arquivos) + '</select>' + html.split('</select>')[1])


#POST
else:
	#Variáveis de POST
	form = cgi.FieldStorage()

	#Criterio e Pesquisa
	if ' ' in form['pesquisa'].value: parametros = form['pesquisa'].value.split(' ', 1)[1]
	if not re.match('^\d+$', form['pesquisa'].value.split(' ')[0]):
		criterio = '1'
		parametros = form['pesquisa'].value
		print('<script>window.alert("Critério não especificado. Utilizando expressão regular (critério 1).")</script>')
	else:
		criterio = form['pesquisa'].value.split(' ')[0]

	#Checa quantidade de critérios
	if int(criterio) > int(open('/interrogar-ud/max_crit.txt', 'r').read().split()[0]):
		print('em desenvolvimento')
		exit()

	#Arquivo UD, Nome, Data, Link
	arquivo_ud = '/interrogar-ud/conllu/' + form["conllu"].value
	ud = form["conllu"].value
	nome = 'teste' if form['meth'].value == 'teste' else form['nome'].value
	data = str(datetime.now()).replace(' ','_').split('.')[0]
	link = '/interrogar-ud/resultados/' + slugify(nome) + '_' + data + '.html'

	#Ocorrências da pesquisa Interrogar_UD.py
	interrogarud = interrogar_UD.main(arquivo_ud, int(criterio), parametros)
	lista_ocorrencias = interrogarud['output']
	print('Total: ' + str(len(lista_ocorrencias)))
	ocorrencias = str(len(lista_ocorrencias))

	#Abre o arquivo conllu
	conllu_completo = open(arquivo_ud, 'r').read().split('\n\n')

	#Abre o arquivo LINK1 e dá replace no FILTRAR e CONLLU
	html = open('/interrogar-ud/resultados/link1.html', 'r').read()
	html = html.replace('/cgi-bin/filtrar.cgi', '/cgi-bin/filtrar.cgi?html=' + slugify(nome) + '_' + data + '&udoriginal=' + ud)
	html = html.replace('/cgi-bin/conllu.cgi', '/cgi-bin/conllu.cgi?html=/interrogar-ud/resultados/' + slugify(nome) + '_' + data + '.html')

	#código em si
	html1 = html.split('<!--SPLIT-->')[0]
	html2 = html.split('<!--SPLIT-->')[1]

	#PARA CADA OCORRÊNCIA DA PESQUISA
	for i, ocorrencia in enumerate(lista_ocorrencias):
		print(str(i+1) + '/' + str(len(lista_ocorrencias)))
		ocorrencia = ocorrencia.replace('<b>','@BOLD').replace('</b>','/BOLD').replace('<font color="' + tabela['yellow'] + '">','@YELLOW/').replace('<font color="' + tabela['red'] + '">','@RED/').replace('<font color="' + tabela['cyan'] + '">','@CYAN/').replace('<font color="' + tabela['blue'] + '">','@BLUE/').replace('<font color="' + tabela['purple'] + '">','@PURPLE/').replace('</font>','/FONT').replace('<','&lt;').replace('>','&gt;')
		ocorrencia_limpa = ocorrencia.replace('@BOLD', '').replace('/BOLD', '').replace('@YELLOW/', '').replace('@RED/', '').replace('@CYAN/', '').replace('@BLUE/', '').replace('@PURPLE/', '').replace('/FONT', '').replace('&lt;', '<').replace('&gt;', '>')

		#PROCURA SENTID E TEXT
		if '# sent_id = ' in ocorrencia:
			sentid = ocorrencia.split('# sent_id = ')[1].split('\n')[0]
		else: sentid = ''
		if '# text = ' in ocorrencia:
			text = ocorrencia.split('# text = ')[1].split('\n')[0]
		else: text = ''

		#ADICIONA O CONTAINER
		html1 = html1 + '''<div class="container">
<p>'''+str(i+1)+''' / '''+ocorrencias+'''</p>'''
		#SENTID
		if sentid != '': html1 += '''<p><input class="cb" id="checkbox_'''+str(i+1)+'''" style="margin-left:0px;" title="Selecionar sentença para filtragem" type="checkbox"> '''+sentid.replace('/BOLD','</b>').replace('@BOLD','<b>')+'''</p>'''
		#OPÇÕES
		html1 += '''<form action="/cgi-bin/inquerito.py?conllu=''' + ud + '''" target="_blank" method="POST" id="form_'''+str(i+1)+'''"><input type=hidden name=sentid value="''' + sentid.replace('@BOLD', '').replace('/BOLD', '').replace('@YELLOW/', '').replace('@PURPLE/', '').replace('@BLUE/', '').replace('@RED/', '').replace('@CYAN/', '').replace('/FONT', '') + '''"><input type=hidden name=occ value="''' + ocorrencias + '''"><input type="hidden" name="textheader" value="''' + text.replace('/BOLD','').replace('@BOLD','').replace('@YELLOW/', '').replace('@PURPLE/', '').replace('@BLUE/', '').replace('@RED/', '').replace('@CYAN/', '').replace('/FONT', '') + '''"><input type=hidden name="nome_interrogatorio" value="''' + nome.replace('"', '&quot;') + '''"><input type=hidden name="link_interrogatorio" value="''' + link + '''"></form>'''
		html1 += '''<form action="/cgi-bin/udpipe.py?conllu=''' + ud + '''" target="_blank" method="POST" id="udpipe_'''+str(i+1)+'''"><input type="hidden" name="textheader" value="''' + text.replace('/BOLD','').replace('@BOLD','').replace('@YELLOW/', '').replace('@PURPLE/', '').replace('@BLUE/', '').replace('@RED/', '').replace('@CYAN/', '').replace('/FONT', '') + '''"></form>'''
		html1 += '<form action="/cgi-bin/draw_tree.py?conllu=' + ud + '" target="_blank" method="POST" id="tree_' + str(i+1) + '"><input type=hidden name=sent_id value="' + sentid.replace('@BOLD', '').replace('/BOLD', '').replace('@YELLOW/', '').replace('@PURPLE/', '').replace('@BLUE/', '').replace('@RED/', '').replace('@CYAN/', '').replace('/FONT', '') + '"><input type=hidden name=text value="' + text.replace('@BOLD', '').replace('/BOLD', '').replace('@YELLOW/', '').replace('@PURPLE/', '').replace('@BLUE/', '').replace('@RED/', '').replace('@CYAN/', '').replace('/FONT', '') + '"></form>'
		#TEXT
		html1 += '''<p><span id="text_'''+str(i+1)+'''">'''+ text.replace('/BOLD','</b>').replace('@BOLD','<b>').replace('@YELLOW/', '<font color="' + tabela['yellow'] + '">').replace('@PURPLE/', '<font color="' + tabela['purple'] + '">').replace('@BLUE/', '<font color="' + tabela['blue'] + '">').replace('@RED/', '<font color="' + tabela['red'] + '">').replace('@CYAN/', '<font color="' + tabela['cyan'] + '">').replace('/FONT', '</font>')+ '''</span></p>
<p>'''

		#CONTEXTO
		if sentid != '' and text != '':
			if '-' in sentid or re.search('^\d+$', sentid):
				temcontexto = True
			else:
				temcontexto = False
		else:
			temcontexto = False

		if temcontexto:
			html1 += '''<input id="contexto_'''+str(i+1)+'''" value="Mostrar contexto" onclick="contexto('divcontexto_'''+str(i+1)+'''', 'contexto_'''+str(i+1)+'''')" style="margin-left:0px" type="button"> <input id="mostrar_'''+str(i+1)+'''" class="anotacao" value="Mostrar anotação" onclick="mostrar('div_'''+str(i+1)+'''', 'mostrar_'''+str(i+1)+'''')" style="margin-left:0px" type="button"> <input id="opt_'''+str(i+1)+'''" class="opt" value="Mostrar opções" onclick="mostraropt('optdiv_'''+str(i+1)+'''', 'opt_'''+str(i+1)+'''')" style="margin-left:0px" type="button"> <input type="button" value="Abrir inquérito" onclick='inquerito("form_'''+str(i+1)+'''")'>'''
		else:
			html1 += '''<input id="mostrar_'''+str(i+1)+'''" class="anotacao" value="Mostrar anotação" onclick="mostrar('div_'''+str(i+1)+'''', 'mostrar_'''+str(i+1)+'''')" style="margin-left:0px" type="button"> <input id="opt_'''+str(i+1)+'''" class="opt" value="Mostrar opções" onclick="mostraropt('optdiv_'''+str(i+1)+'''', 'opt_'''+str(i+1)+'''')" style="margin-left:0px" type="button"> <input type="button" value="Abrir inquérito" onclick='inquerito("form_'''+str(i+1)+'''")'>'''

		html1 += '''</p>'''

		#CONTEXTO
		if temcontexto:
			if '-' in sentid:
				sentnum = int(sentid.rsplit('-', 1)[1].split()[0].split('/')[0])
				sentnome = sentid.rsplit('-', 1)[0]
				contexto1 = ''
				contexto2 = ''
				if sentnum == 1:
					contexto1 = '.'
				for sentence in conllu_completo:
					if '# sent_id = ' in sentence and '# text = ' in sentence:
						if contexto1 != '.':
							if sentence.split('# sent_id = ')[1].rsplit('-', 1)[0] == sentnome and int(sentence.split('# sent_id = ')[1].rsplit('-', 1)[1].split('\n')[0]) == sentnum -1:
								contexto1 = sentence.split('# text = ')[1].split('\n')[0]
						if sentence.split('# sent_id = ')[1].rsplit('-', 1)[0] == sentnome and int(sentence.split('# sent_id = ')[1].rsplit('-', 1)[1].split('\n')[0]) == sentnum +1:
							contexto2 = sentence.split('# text = ')[1].split('\n')[0]
						if (contexto1 != '' or contexto1 == '.') and contexto2 != '':
							break
				html1 += '''<p id="divcontexto_'''+str(i+1)+'''" style="display:none">''' + contexto1 + ' ' + text.replace('/BOLD','</b>').replace('@BOLD','<b>').replace('@YELLOW/', '<font color="' + tabela['yellow'] + '">').replace('@PURPLE/', '<font color="' + tabela['purple'] + '">').replace('@BLUE/', '<font color="' + tabela['blue'] + '">').replace('@RED/', '<font color="' + tabela['red'] + '">').replace('@CYAN/', '<font color="' + tabela['cyan'] + '">').replace('/FONT', '</font>') + ' ' + contexto2 + '''</p>\n'''

			#NOT - in sentid
			else:
				try:
					sentnum = int(sentid)
					contexto1 = ''
					contexto2 = ''
					if sentnum == 1:
						contexto1 = '.'
					for sentence in conllu_completo:
						if '# sent_id = ' in sentence and '# text = ' in sentence:
							if contexto1 != '.':
								if int(sentence.split('# sent_id = ')[1].split('\n')[0]) == sentnum -1:
									contexto1 = sentence.split('# text = ')[1].split('\n')[0]
							if int(sentence.split('# sent_id = ')[1].split('\n')[0]) == sentnum +1:
								contexto2 = sentence.split('# text = ')[1].split('\n')[0]
							if (contexto1 != '' or contexto1 == '.') and contexto2 != '':
								break
					html1 += '''<p id="divcontexto_'''+str(i+1)+'''" style="display:none">''' + contexto1 + ' ' + text.replace('/BOLD','</b>').replace('@BOLD','<b>').replace('@YELLOW/', '<font color="' + tabela['yellow'] + '">').replace('@PURPLE/', '<font color="' + tabela['purple'] + '">').replace('@BLUE/', '<font color="' + tabela['blue'] + '">').replace('@RED/', '<font color="' + tabela['red'] + '">').replace('@CYAN/', '<font color="' + tabela['cyan'] + '">').replace('/FONT', '</font>') + ' ' + contexto2 + '''</p>\n'''
				except:
					pass

		#Fim contexto e anotação
		#Opções
		html1 += '''<p style="display:none" id="optdiv_''' + str(i+1) + '''"><a style="cursor:pointer" onclick='filtraragora("'''+str(i+1)+'''")'>Remover sentença</a><br>'''
		html1 += '''<a style="cursor:pointer" onclick='anotarudpipe("udpipe_'''+str(i+1)+'''")'>Anotar no UDPipe</a><br>'''
		html1 += '''<a style="cursor:pointer" onclick='drawtree("tree_'''+str(i+1)+'''")'>Visualizar árvore</a>'''
		html1 += '''</p>'''

		#ANOTAÇÃO
		html1 += '''\n<pre id="div_'''+str(i+1)+'''" style="display:none">''' + ocorrencia.replace('/BOLD','</b>').replace('@BOLD','<b>').replace('@YELLOW/', '<font color="' + tabela['yellow'] + '">').replace('@PURPLE/', '<font color="' + tabela['purple'] + '">').replace('@BLUE/', '<font color="' + tabela['blue'] + '">').replace('@RED/', '<font color="' + tabela['red'] + '">').replace('@CYAN/', '<font color="' + tabela['cyan'] + '">').replace('/FONT', '</font>') + '''</pre>'''

		html1 += '</div>\n'


	html = html1 + html2

	#<!--script-->
	html1 = html.split('<!--script-->')[0]
	html2 = html.split('<!--script-->')[1]
	html1 += '<form method="POST" action="/cgi-bin/inquerito.py?action=script&executar=sim" target="_blank">'
	html1 += '''<input type=hidden name="nome_interrogatorio" value="''' + nome.replace('"', '&quot;') + '''"><input type=hidden name=occ value="''' + ocorrencias + '''"><input type=hidden name="link_interrogatorio" value="''' + link + '''"><input type=hidden name="conllu" value="''' + ud + '''">'''
	html1 += '<input type=text name="script" list="lista" required><datalist id="lista">'
	if not os.path.isdir('/interrogar-ud/scripts/'):
		os.mkdir('/interrogar-ud/scripts')
	for item in os.listdir('/interrogar-ud/scripts/'):
		if '.py' in item and not 'estrutura_dados' in item:
			html1 += '<option value="' + item + '">' + item + '</option>'
	html1 += '</datalist> <input type="submit" value="Executar"></form>'
	html = html1 + html2

	#title
	novo_html = re.sub(re.escape('<title>link de pesquisa 1 (203): Interrogatório</title>'), '<title>' + nome.replace('\\', '\\\\').replace('<', '&lt;').replace('>', '&gt;') + ' (' + ocorrencias + '): Interrogatório</title>', html)

	#h1 - NOME DA QUERY
	novo_html = re.sub(re.escape('<h1><span id="combination">link de pesquisa 1</span> (203)</h1>'), '<h1><span id="combination">' + nome.replace('\\', '\\\\').replace('<', '&lt;').replace('>', '&gt;') + '</span> (' + ocorrencias + ')</h1><br>Casos: ' + str(interrogarud['casos']), novo_html)

	#h2 - METADADOS DA QUERY
	criterios = open('/interrogar-ud/criterios.txt', 'r').read().split('!@#')
	novo_html = re.sub(re.escape('<p>critério y#z#k&nbsp;&nbsp;&nbsp; arquivo_UD&nbsp;&nbsp;&nbsp; <span id="data">data</span>&nbsp;&nbsp;&nbsp;'), '<p><div class="tooltip">' + criterio + ' ' + parametros.replace('\\','\\\\').replace('<','&lt;').replace('>','&gt;') + '<span class="tooltiptext">' + criterios[int(criterio)].replace('\\','\\\\').split('<h4>')[0] + '</span></div> &nbsp;&nbsp;&nbsp;&nbsp; ' + ud + ' &nbsp;&nbsp;&nbsp;&nbsp; <span id="data">' + data.replace('_', ' ') + '</span> &nbsp;&nbsp;&nbsp;&nbsp; ', novo_html)

	#APAGAR.CGI
	novo_html = novo_html.replace('id="apagar_link" value="link1"', 'id="apagar_link" value="' + slugify(nome) + '_' + data + '"')

	open(link, 'w').write(novo_html)

	queries = [link + '\t' + nome + '\t' + ocorrencias + '\t' + criterio + '\t' + parametros + '\t' + ud + '\t' + data]
	queries.extend(open('/interrogar-ud/queries.txt', 'r').read().splitlines())

	open('/interrogar-ud/queries.txt', 'w').write("\n".join(queries))

	print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body onload="redirect()"><script>function redirect() { window.location = "'+link+'" }</script></body>')


