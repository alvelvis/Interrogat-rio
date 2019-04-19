# -*- coding: utf-8 -*-

import sys
from estrutura_dados import LerUD
import re
import os
from subprocess import call
import estrutura_ud

try:
		import pandas as pd
except:
		try:
				from pip import main as pipmain
		except:
				print('Instale a biblioteca "pandas" e tente novamente.')
				exit()
		else:
				pipmain(['install', 'pandas'])
				print('Biblioteca "pandas" instalada com sucesso!')
				exit()

feats = {
				1: "ID",
				2: "FORM",
				3: "LEMMA",
				4: "UPOSTAG",
				5: "XPOSTAG",
				6: "FEATS",
				7: "HEAD",
				8: "DEPREL",
				9: "DEPS",
				10: "MISC",
}

def get_list(conllu1, conllu2, coluna):
		lista_coluna1 = list()
		lista_coluna2 = list()
		solitários1 = list()
		solitários2 = list()

		#Sentença por sentença do conllu1
		for sentença in conllu1:
				sentença_length = 0
				for linha in sentença:
						#Encontrou o text_header da sentença
						if '# text = ' in linha:
								text_header = linha
						#Cresce o tamanho de tokens da sentença
						if isinstance(linha, list):
								sentença_length += 1
				#Começa a alinhar com o conllu2 para ver se a sentença também tem lá
				tem = False
				for subsentença in conllu2:
						sentença_correta = False
						subsentença_length = 0
						for sublinha in subsentença:
								#Encontrou a sentença cujo text_header é igual
								if sublinha == text_header:
										sentença_correta = True
								#Cresceu o tamanho de tokens da sentença correta
								if sentença_correta and isinstance(sublinha, list):
										subsentença_length += 1
						#Se tiver uma sentença igual em text_header e em tamanho, tem = True
						if sentença_correta and subsentença_length == sentença_length:
								tem = True
								for sublinha in subsentença:
									if isinstance(sublinha, list):
										lista_coluna2.append(sublinha[coluna-1])
				#Se encontrou sentença igual em conllu2, append!
				if tem:
						for linha in sentença:
								if isinstance(linha, list):
										lista_coluna1.append(linha[coluna-1])
				#Se não encontrou, solitários.append
				else:
						solitários1.append(text_header)

		#Procurar os solitários2
		for sentença in conllu2:
				sentença_length = 0
				for linha in sentença:
						if '# text =' in linha:
								text_header = linha
						if isinstance(linha, list):
								sentença_length += 1
				tem = False
				for subsentença in conllu1:
						sentença_correta = False
						subsentença_length = 0
						for sublinha in subsentença:
								if sublinha == text_header:
										sentença_correta = True
								if sentença_correta and isinstance(sublinha, list):
										subsentença_length += 1
						if sentença_correta and subsentença_length == sentença_length:
								tem = True
				if not tem:
						solitários2.append(text_header)

		return {'matriz_1': lista_coluna1, 'matriz_2': lista_coluna2, 'solitários_1': solitários1, 'solitários_2': solitários2}


def gerar_HTML(matriz, ud1, ud2, col, output, codificação):
		script = 'cat | python3 conll18_ud_eval.py -v "' + matriz.split('\n\n')[0].splitlines()[1].split(': ' ,1)[1] + '" "' + matriz.split('\n\n')[0].splitlines()[2].split(': ' ,1)[1] + '" > metrica.txt'
		call(script, shell=True)
		metrics = open("metrica.txt", 'r').read()
		with open(output + "_results.txt", "r") as f:
			resultados_cru = f.read()
		with open(output + "_sentence.txt", "r") as f:
			sentence_accuracy = f.read()

		resultados = "<table><tr><th>Acurácia por categoria gramatical</th></tr>"
		for linha in resultados_cru.splitlines():
			resultados += "<tr>"
			for item in linha.split():
				resultados += "<td>" + item + "</td>"
			resultados += "</tr>"
		resultados += "</table>"

		html = ['<html><head><meta charset="'+codificação+'" name="viewport" content="width=device-width, initial-scale=1.0" ><link href="style.css" rel="stylesheet" type="text/css"><link href="http://fonts.googleapis.com/css?family=Lato" rel="stylesheet" type="text/css"></head><body><div class="header">']
		html.append('<h1>'+output+'</h1><br><span id="topo"><h3>' + "\n".join(matriz.split('\n\n')[0].splitlines()[1:]) + '''</h3></span></div><div class="content"><center><table><th>Métricas oficiais</th><tr><td><pre>'''+metrics+'''</pre></td></tr></table><br>''' + sentence_accuracy + '''<br>''' + resultados + '''</center></div><!--div class="tab"><button class="tablinks" onclick="openCity(event, 'Dados')">Métricas oficiais</button><button class="tablinks" onclick="openCity(event, 'Matriz')">Matriz de confusão</button></div><div class="tabcontent" id="Matriz"--><pre><table id="t01">''')

		tiposy = dict()
		tiposx = dict()
		for i, linha in enumerate("\n".join(matriz.split('\n\n')[1:]).split('#!$$')[0].split('\n')[2:-1]):
				tiposy[i+2] = linha.split(' ')[0]
		for i, coluna in enumerate("\n".join(matriz.split('\n\n')[1:]).split('#!$$')[0].split('\n')[0].split()[1:-1]):
				tiposx[i+1] = coluna
		y = 0

		linha_html = ""
		for linha in "\n".join(matriz.split('\n\n')[1:]).split('#!$$')[0].split('\n'):
				if linha.strip() != '':
						linha_html += '<tr><td>' + linha.split(' ')[0] + '</td>'
						if y == 0 or y == 1:
								for x, coluna in enumerate(linha.split()[1:]):
										#linha_html += '&#09;' + coluna
										linha_html += '<td>' + coluna + '</td>'
								y += 1
						elif y < len(tiposy):
								for x, coluna in enumerate(linha.split()[1:-1]):
										#linha_html += '&#09;' + '<a href="' + output + '_html/' + tiposy[y] + '-' + tiposx[x+1] + '.html">' + coluna + '</a>'
										linha_html += '<td>' + '<a href="' + output + '_html/' + tiposy[y] + '-' + tiposx[x+1] + '.html">' + coluna + '</a>' + '</td>'
								y += 1
								#linha_html += '&#09;' + linha.split()[-1]
								linha_html += '<td>' + linha.split()[-1] + '</td>'
						elif y == len(tiposy):
								for x, coluna in enumerate(linha.split()[1:]):
										#linha_html += '&#09;' + coluna
										linha_html += '<td>' + coluna + '</td>'
						linha_html += '</tr>'

		html.append(linha_html + '</table></pre>')

		solitários = dict()
		for i, grupo in enumerate(matriz.split('#!$$')[1:]):
				grupo = [x for x in grupo.splitlines() if x]
				html.append('<div class="container"><b>' + grupo[0] + ' (' + str(len(grupo[1:])) + ''')</b> <input type="button" id="botao''' + str(i) + '''" value="Mostrar" onClick="ativa('solitary''' + str(i) + '''', 'botao''' + str(i) + '''')" class="btn-gradient blue mini"><br>''')
				html.append("<div id='solitary" + str(i) + "' style='display:none'>")
				for linha in grupo[1:]:
						if linha.strip() != '':
								html.append(linha)
				html.append("</div></div>")

		sentenças = dict()
		for sentença in ud1:
				sentença_id = ''
				tamanho_sentença = 0
				for linha in sentença:
						if '# text = ' in linha:
								sentença_header = linha
						if '# sent_id = ' in linha:
								sentença_id = linha
						if isinstance(linha, list):
								tamanho_sentença += 1
				for subsentença in ud2:
						subsentença_correta = False
						tamanho_subsentença = 0
						for sublinha in subsentença:
								if '# text = ' in sublinha and sublinha == sentença_header:
										subsentença_correta = True
								if sentença_id == '' and '# sent_id = ' in sublinha:
										sentença_id = sublinha
								if isinstance(sublinha, list):
										tamanho_subsentença += 1
						if subsentença_correta and tamanho_sentença == tamanho_subsentença:
								sentença_limpo = [x for x in sentença if isinstance(x, list)]
								subsentença_limpo = [x for x in subsentença if isinstance(x, list)]
								sentença_limpo_string = [x for x in sentença if isinstance(x, list)]
								subsentença_limpo_string = [x for x in subsentença if isinstance(x, list)]
								for l, linha in enumerate(sentença_limpo_string):
										if isinstance(linha, list):
												sentença_limpo_string[l] = "&#09;".join(sentença_limpo_string[l])
								sentença_limpo_string = "\n".join(sentença_limpo_string)
								for l, linha in enumerate(subsentença_limpo_string):
										if isinstance(linha, list):
												subsentença_limpo_string[l] = "&#09;".join(subsentença_limpo_string[l])
								subsentença_limpo_string = "\n".join(subsentença_limpo_string)
								for k in range(len(sentença_limpo)):
										coluna1 = sentença_limpo[k][col-1]
										coluna2 = subsentença_limpo[k][col-1]
										palavra = sentença_limpo[k][1]
										if not coluna1 + '-' + coluna2 in sentenças:
												sentenças[coluna1 + '-' + coluna2] = [(sentença_id, re.sub(r'\b(' + re.escape(palavra) + r')\b', '<b>' + palavra +'</b>', sentença_header), sentença_limpo_string.replace("&#09;".join(sentença_limpo[k]), '<b>' + "&#09;".join(sentença_limpo[k]) + '</b>'), subsentença_limpo_string.replace("&#09;".join(subsentença_limpo[k]), '<b>' + "&#09;".join(subsentença_limpo[k]) + '</b>'))]
										else: sentenças[coluna1+'-'+coluna2].append((sentença_id, re.sub(r'\b(' + re.escape(palavra) + r')\b', '<b>' + palavra + '</b>', sentença_header), sentença_limpo_string.replace("&#09;".join(sentença_limpo[k]), '<b>' + "&#09;".join(sentença_limpo[k]) + '</b>'), subsentença_limpo_string.replace("&#09;".join(subsentença_limpo[k]), '<b>' + "&#09;".join(subsentença_limpo[k]) + '</b>')))

		open(output + '.html', 'w', encoding=codificação).write("<br>".join(html).replace('\n','<br>') + '''</div></div></body></html>

<script>
function ativa(nome, botao){
var div = document.getElementById(nome)
if (div.style.display == 'none') {
document.getElementById(botao).value='Esconder'
div.style.display = 'block'
} else {
div.style.display = 'none'
document.getElementById(botao).value='Mostrar'
}
}
function carregar_version(){
var link_combination = document.getElementById("carregar_edit").value.split("/")
window.location = window.location.href.split(".html")[0] + "_html/" + link_combination[link_combination.length-1].split("?")[0] + "?" + document.getElementById("carregar_edit").value.split("?")[1]
}
function openCity(evt, cityName) {
	// Declare all variables
	var i, tabcontent, tablinks;

	// Get all elements with class="tabcontent" and hide them
	tabcontent = document.getElementsByClassName("tabcontent");
	for (i = 0; i < tabcontent.length; i++) {
		tabcontent[i].style.display = "none";
	}

	// Get all elements with class="tablinks" and remove the class "active"
	tablinks = document.getElementsByClassName("tablinks");
	for (i = 0; i < tablinks.length; i++) {
		tablinks[i].className = tablinks[i].className.replace(" active", "");
	}

	// Show the current tab, and add an "active" class to the button that opened the tab
	document.getElementById(cityName).style.display = "block";
	evt.currentTarget.className += " active";
}
</script>''')

		#Páginas independentes
		for combinação in sentenças:
				html = ['<html><form><head><meta charset="'+codificação+'" name="viewport" content="width=device-width, initial-scale=1.0" /><style>input[name=maior] { width: 400; }</style><link href="../style.css" rel="stylesheet" type="text/css"><link href="http://fonts.googleapis.com/css?family=Lato" rel="stylesheet" type="text/css"></head><body onLoad="carregar()"><div class="header">'] #<form action="../matriz_cgi.py?output='+output+'&combination='+combinação+'&encoding='+codificação+'" method="post">
				html.append('<h1>'+output+'</h1><br><span id="topo"><h3>' + matriz.split('\n\n')[0] + '</span></h3></div><div class="content"><h3><a href="../' + output + '.html">Voltar</a></h3>')
				if not os.path.isdir(output + '_html'):
						os.mkdir(output + '_html')
				html.append('<h1><span id="combination">' + combinação + '</span> (' + str(len(sentenças[combinação])) + ')</h1><hr><br>' + ''' <input type="button" onclick="enviar('2')" id="salvar_btn" class="btn-gradient orange mini" style="margin-left:0px" value="Gerar link para a versão atual"> <input type="button" class="btn-gradient green mini" onclick="copiar_frases()" id="copiar_btn" value="Copiar sent_id das frases" style="margin-left:0px"> <input id="link_edit2" type="text" style="display:none"> <div id="gerado2" style="display:none"><b>Link gerado!</b></div><br><br>''')

				carregamento_comment = list()
				carregamento_check = list()
				for i, sentença in enumerate(sentenças[combinação]):
						carregamento_check.append('check1_'+str(i))
						carregamento_check.append('check2_'+str(i))
						carregamento_comment.append('comment'+str(i))
						html.append('<div class="container">' + str(i+1) + ' / ' + str(len(sentenças[combinação])) + '<br><br>' + sentença[0] + '<br><br>' + '''<input type="hidden" name="copiar_id" id="''' + str(i) + '''" value="''' + sentença[0].replace('/BOLD','').replace('@BOLD','').replace('@YELLOW/', '').replace('@PURPLE/', '').replace('@BLUE/', '').replace('@RED/', '').replace('@CYAN/', '').replace('/FONT', '') + '''">''' + sentença[1] + '<br><br><input type="checkbox" style="margin-left:0px" id="check1_'+str(i)+'" >' + combinação.split('-')[0] + ' <input type="checkbox" id="check2_'+str(i)+'" >' + combinação.split('-')[1] + ' - Comentários: <input type="text" id="comment'+str(i)+'" name="maior" >')
						html.append('''<br><input type="button" id="botao1''' + combinação + str(i) + '''" style="margin-left:0px" value="Mostrar UD[1]" onClick="ativa1('sentence1''' + combinação + str(i) + '''', 'botao1''' + combinação + str(i) + '''')" > <input type="button" id="botao2''' + combinação + str(i) + '''" value="Mostrar UD[2]" onClick="ativa2('sentence2''' + combinação + str(i) + '''', 'botao2''' + combinação + str(i) + '''')">''')
						html.append("<div id='sentence1" + combinação + str(i) + "' style='display:none'><b><br>UD[1]:</b>")
						html.append("<pre>" + sentença[2].replace('<','&lt;').replace('>','&gt;') + "</pre></div><div id='sentence2" + combinação + str(i) + "' style='display:none'><br><b>UD[2]:</b>")
						html.append("<pre>" + sentença[3].replace('<','&lt;').replace('>','&gt;') + '</pre></div></div>')

				html = "<br>".join(html).replace('\n','<br>') + '''<br><input type="button" class="btn-gradient orange" onclick="enviar('1')" id="salvar_btn" value="Gerar link para a versão atual" style="margin-left:0px"> <input id="link_edit1" type="text" style="display:none"> <div id="gerado1" style="display:none"><b>Link gerado!</b></div><br><h3><a href="../''' + output + '''.html">Voltar</a></h3></div></body></form></html>

<script>
function escapeRegExp(string) {
	return string.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&').replace('&amp;', '.'); // $& means the whole matched string
}
String.prototype.rsplit = function(sep, maxsplit) {
	var split = this.split(sep);
	return maxsplit ? [ split.slice(0, -maxsplit).join(sep) ].concat(split.slice(-maxsplit)) : split;
}
function copiar_frases(){
	document.getElementById("link_edit2").value = "";
	document.getElementById("link_edit2").style.display = "inline";
	
	var sentids, i;
	sentids = document.getElementsByName("copiar_id");
	for (i = 0; i < sentids.length; i++) {
		document.getElementById("link_edit2").value = document.getElementById("link_edit2").value + "^" + sentids[i].value + "$|";
	}
	document.getElementById("link_edit2").value = document.getElementById("link_edit2").value.rsplit('|',1)[0];
}
function carregar_version(){
window.location = window.location.href.split("?")[0] + "?" + document.getElementById("carregar_edit").value.split("?")[1]
}
function ativa1(nome, botao){
var div = document.getElementById(nome)
if (div.style.display == 'none') {
document.getElementById(botao).value='Esconder UD[1]'
div.style.display = 'block'
} else {
div.style.display = 'none'
document.getElementById(botao).value='Mostrar UD[1]'
}
}
function ativa2(nome, botao){
var div = document.getElementById(nome)
if (div.style.display == 'none') {
document.getElementById(botao).value='Esconder UD[2]'
div.style.display = 'block'
} else {
div.style.display = 'none'
document.getElementById(botao).value='Mostrar UD[2]'
}
}
function gerado_false(id) {
document.getElementById("gerado"+id).style.display = "none"
}
'''
				script_onload = ['function carregar() {','let url_href = window.location.href','let url = new URL(url_href)']
				for item in carregamento_comment:
						script_onload.append('document.getElementById("'+item+'").value = url.searchParams.get("'+item+'")')
				for item in carregamento_check:
						script_onload.append('if (url.searchParams.get("'+item+'") == "true") { document.getElementById("'+item+'").checked = url.searchParams.get("'+item+'") }')
				script_onload.append('}')

				link = '?'
				script_enviar = ['''
function enviar(id) {
document.getElementById("gerado"+id).style.display = "inline"
setTimeout("gerado_false("+id+")", 1000)
document.getElementById("link_edit"+id).style.display = "inline"''']

				link = '?'
				for item in carregamento_comment:
						link += item + '=" + document.getElementById("' + item + '").value.replace(/\?/g, "~").replace(/\&/g, "~").replace(/\//g,"~") + "&'
				for item in carregamento_check:
						link += item + '=" + document.getElementById("' + item + '").checked + "&'

				script_enviar.append('document.getElementById("link_edit"+id).value = window.location.href.split("?")[0] + "' + link + '"')
				script_enviar.append('}')


				html += "\n".join(script_onload) + "\n".join(script_enviar) + '\n</script>'

				open(output + '_html/' + combinação + '.html', 'w', encoding=codificação).write(html)

def get_percentages(ud1, ud2, output, coluna):
	with open(ud1, "r") as f:
		golden_dict = {}
		for i, sent in enumerate(f.read().split("\n\n")):
			sentence = estrutura_ud.Sentence()
			sentence.build(sent)
			golden_dict[str(i+1)] = sentence

	with open(ud2, "r") as f:
		system = estrutura_ud.Corpus()
		system.build(f.read())

	dicionario = {}
	for sentid, sentence in golden_dict.items():
		for t, token in enumerate(sentence.tokens):
			if not token.deprel in dicionario:
				dicionario[token.deprel] = [0, 0, 0]
			dicionario[token.deprel][0] += 1
			if system.sentences[sentid].tokens[t].deprel == token.deprel:
				dicionario[token.deprel][1] += 1

	sent_accuracy = [0, 0]
	for sentid, sentence in golden_dict.items():
		if sentid in system.sentences and len(sentence.tokens) == len(system.sentences[sentid].tokens):
			sent_accuracy[0] += 1
			acertos = 0
			for t, token in enumerate(sentence.tokens):
				if system.sentences[sentid].tokens[t].upos == token.upos and system.sentences[sentid].tokens[t].dephead == token.dephead and system.sentences[sentid].tokens[t].deprel == token.deprel:
					acertos += 1
			if acertos == len(sentence.tokens):
				sent_accuracy[1] += 1
				print(sentid)
	sentence_accuracy = "<table><tr><th>Acurácia por sentença</th></tr><tr><th>Sentenças comparáveis</th><th>Sentenças corretas</th><th>Número relativo</th></tr><tr><td>{0}</td><td>{1}</td><td>{2}</td></tr></table>".format(sent_accuracy[0], sent_accuracy[1], str((sent_accuracy[1]/sent_accuracy[0])*100) + "%")
	with open(output + "_sentence.txt", "w") as f:
		f.write(sentence_accuracy)

	csv = ["{0:20} {1:10} {2:10} {3:}".format("DEPREL", "GOLDEN", "ACERTOS", "PORCENTAGEM")]
	for classe in dicionario:
		dicionario[classe][2] = (dicionario[classe][1] / dicionario[classe][0]) * 100
		csv.append("{0:20} {1:10} {2:10} {3:}".format(classe, str(dicionario[classe][0]), str(dicionario[classe][1]), str(dicionario[classe][2]) + "%"))

	with open(output + "_results.txt", "w") as f:
		f.write("\n".join(csv))


def main(ud1, ud2, output, coluna = 4):	
	conllu1 = LerUD(ud1)
	conllu2 = LerUD(ud2)
	lista_conllu = get_list(conllu1, conllu2, coluna)
	lista_conllu1 = lista_conllu['matriz_1']
	lista_conllu2 = lista_conllu['matriz_2']
	pd.options.display.max_rows = None
	pd.options.display.max_columns = None
	pd.set_option('display.expand_frame_repr', False)
	saída = list()
	saída.append('Col ' + str(coluna)+': ' + feats[coluna])
	saída.append('UD[1]: ' + ud1)
	saída.append('UD[2]: ' + ud2 + '\n')
	saída.append(str(pd.crosstab(pd.Series(lista_conllu1), pd.Series(lista_conllu2), rownames=['UD[1]'], colnames=['UD[2]'], margins=True)))
	saída.append('\n')
	saída.append('#!$$ Sentenças de UD[1] que não foram encontradas em UD[2]:\n')
	for item in lista_conllu['solitários_1']:
			saída.append(item)
	saída.append('\n#!$$ Sentenças de UD[2] que não foram encontradas em UD[1]:\n')
	for item in lista_conllu['solitários_2']:
			saída.append(item)

		#Output
	if ':' in output: codificação_saída = output.split(':')[1]
	else: codificação_saída = 'utf8'
	output = output.split(':')[0]

	get_percentages(ud1, ud2, output, coluna)

		#Gera os arquivos HTML
	gerar_HTML("\n".join(saída), conllu1, conllu2, coluna, output, codificação_saída)
	#Gera o arquivo "txt" (apenas a matriz)
	open(output, 'w', encoding=codificação_saída).write("\n".join(saída))

if __name__ == '__main__':
	número_de_argumentos_mínimo = 4

	if len(sys.argv) < número_de_argumentos_mínimo +1:
		print('uso: confusão.py ud1.conllu:utf8 ud2.conllu:utf8 saída.txt:utf8 coluna')
		print('Colunas:')
		for i in range(len(feats)):
				print(str(i+1) + ': ' + feats[i+1])
	elif len(sys.argv) >= número_de_argumentos_mínimo +1:
		main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
	else:
		print('Argumentos demais')
