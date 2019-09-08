#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import os
import cgi, cgitb
cgitb.enable()
import re
import estrutura_ud
from estrutura_dados import slugify as slugify
import interrogar_UD
from datetime import datetime
from functions import tabela
import html as web
import time

def main():
	if not os.path.isdir("../interrogar-ud/conllu"):
		os.mkdir("../interrogar-ud/conllu")

	sendRequestInterrogar() if os.environ['REQUEST_METHOD'] != "POST" else sendPOSTInterrogar()


def sendRequestInterrogar():
	arquivosCONLLU = sorted(["<option value='{0}'>{0}</option>".format(slugify(arquivo)) for arquivo in os.listdir("../interrogar-ud/conllu") if arquivo.endswith(".conllu")])
	
	with open("../interrogar-ud/interrogar_UDnew.html", "r") as f:
		paginaHTML = f.read().split("<!--SPLIT-->")

	with open("../interrogar-ud/criterios.txt", "r") as f:
		criteriosBusca = f.read().split("!@#")

	paginaHTML[0] += "\n".join(["<a id=criterio_{0}></a><div class=container-lr>{1}</div>".format(i+1, criterio) for i, criterio in enumerate(criteriosBusca)])

	paginaHTML = "".join(paginaHTML)
	paginaHTML = paginaHTML.split("<select name=\"conllu\">")[0] + "<select name=conllu>" + "\n".join(arquivosCONLLU) + "</select>" + paginaHTML.split("</select>")[1]

	print(paginaHTML)


def sendPOSTInterrogar():
	criterio, parametros, conllu, nomePesquisa = variaveisDePesquisa(cgi.FieldStorage())
	checaQtdCriterios(criterio)

	caminhoCompletoConllu = "../interrogar-ud/conllu/" + conllu
	dataAgora = str(datetime.now()).replace(' ', '_').split('.')[0]
	caminhoCompletoHtml = '../interrogar-ud/resultados/' + slugify(nomePesquisa) + '_' + dataAgora + '.html'

	dicionarioOcorrencias, numeroOcorrencias, casosOcorrencias = realizarBusca(caminhoCompletoConllu, int(criterio), parametros)

	arquivoHtml = montarHtml(caminhoCompletoConllu, caminhoCompletoHtml, nomePesquisa, dataAgora, conllu, criterio, parametros, dicionarioOcorrencias, numeroOcorrencias, casosOcorrencias).montarHtml()

	with open(caminhoCompletoHtml, "w") as f:
		f.write(arquivoHtml)

	queries = [caminhoCompletoHtml + '\t' + nomePesquisa + '\t' + numeroOcorrencias + '\t' + criterio + '\t' + parametros + '\t' + conllu + '\t' + dataAgora]

	with open('../interrogar-ud/queries.txt', 'r') as f:
		queries.extend(f.read().splitlines())

	open('../interrogar-ud/queries.txt', 'w').write("\n".join(queries))

	print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body onload="redirect()"><script>function redirect() { window.location = "'+caminhoCompletoHtml+'" }</script></body>')


def variaveisDePesquisa(form):
	if ' ' in form['pesquisa'].value: parametros = form['pesquisa'].value.split(' ', 1)[1]
	if not re.match(r'^\d+$', form['pesquisa'].value.split(' ')[0]):
		criterio = '1'
		parametros = form['pesquisa'].value
		print('<script>window.alert("Critério não especificado. Utilizando expressão regular (critério 1).")</script>')
	else:
		criterio = form['pesquisa'].value.split(' ')[0]

	conllu = form['conllu'].value
	metodo = form['meth'].value
	nomePesquisa = 'teste' if form['meth'].value == 'teste' else form['nome'].value

	return criterio, parametros, conllu, nomePesquisa


def checaQtdCriterios(criterio):
	with open("../interrogar-ud/max_crit.txt", "r") as f:
		if int(criterio) > int(f.read().strip().split()[0]):
			print('em desenvolvimento')
			exit()


def realizarBusca(caminhoCompletoConllu, criterio, parametros):
	resultadosBusca = interrogar_UD.main(caminhoCompletoConllu, criterio, parametros)
	for n, frase in enumerate(resultadosBusca['output']):
		anotado = estrutura_ud.Sentence(recursivo=False)
		estruturado = estrutura_ud.Sentence(recursivo=False)
		anotado.build(cgi.escape(frase.replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<font color=' + tabela['yellow'] + '>', '@YELLOW/').replace('<font color=' + tabela['red'] + '>', '@RED/').replace('<font color=' + tabela['cyan'] + '>', '@CYAN/').replace('<font color=' + tabela['blue'] + '>', '@BLUE/').replace('<font color=' + tabela['purple'] + '>', '@PURPLE/').replace('</font>', '/FONT')))
		estruturado.build(web.unescape(frase).replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<font color=' + tabela['yellow'] + '>', '@YELLOW/').replace('<font color=' + tabela['red'] + '>', '@RED/').replace('<font color=' + tabela['cyan'] + '">', '@CYAN/').replace('<font color=' + tabela['blue'] + '>', '@BLUE/').replace('<font color=' + tabela['purple'] + '>', '@PURPLE/').replace('</font>', '/FONT').replace('@BOLD', '').replace('/BOLD', '').replace('@YELLOW/', '').replace('@RED/', '').replace('@CYAN/', '').replace('@BLUE/', '').replace('@PURPLE/', '').replace('/FONT', ''))
		
		resultadosBusca['output'][n] = {
			'resultadoAnotado': anotado,
			'resultadoEstruturado': estruturado,
			}

	dicionarioOcorrencias = resultadosBusca['output']
	numeroOcorrencias = str(len(resultadosBusca['output']))
	casosOcorrencias = resultadosBusca['casos']
	#print('Total: ' + numeroOcorrencias)

	return dicionarioOcorrencias, numeroOcorrencias, casosOcorrencias


class montarHtml():

	def __init__(self, caminhoCompletoConllu, caminhoCompletoHtml, nomePesquisa, dataAgora, conllu, criterio, parametros, dicionarioOcorrencias, numeroOcorrencias, casosOcorrencias):
		self.caminhoCompletoConllu = caminhoCompletoConllu
		self.caminhoCompletoHtml = caminhoCompletoHtml
		self.nomePesquisa = nomePesquisa
		self.dataAgora = dataAgora
		self.conllu = conllu
		self.criterio = criterio
		self.parametros = parametros
		self.dicionarioOcorrencias = dicionarioOcorrencias
		self.numeroOcorrencias = numeroOcorrencias
		self.casosOcorrencias = casosOcorrencias
	
	def adicionarHeader(self):
		arquivoHtml = self.arquivoHtml.replace('<title>link de pesquisa 1 (203): Interrogatório</title>', '<title>' + cgi.escape(self.nomePesquisa) + ' (' + self.numeroOcorrencias + '): Interrogatório</title>')
		arquivoHtml = arquivoHtml.replace('<h1><span id="combination">link de pesquisa 1</span> (203)</h1>', '<h1><a id=titulo><span id=combination>' + cgi.escape(self.nomePesquisa) + '</span> (' + self.numeroOcorrencias + ')</a></h1><br>Casos: ' + str(self.casosOcorrencias))

		with open ('../interrogar-ud/criterios.txt', 'r') as f:
			criterios = f.read().split('!@#')
		
		arquivoHtml = arquivoHtml.replace('<p>critério y#z#k&nbsp;&nbsp;&nbsp; arquivo_UD&nbsp;&nbsp;&nbsp; <span id="data">data</span>&nbsp;&nbsp;&nbsp;', '<p><div class=tooltip><span id=expressao>' + self.criterio + ' ' + cgi.escape(self.parametros) + '</span><span class=tooltiptext>' + criterios[int(self.criterio)].split('<h4>')[0] + '</span></div> &nbsp;&nbsp;&nbsp;&nbsp; <span id=corpus>' + self.conllu + '</span> &nbsp;&nbsp;&nbsp;&nbsp; <span id=data>' + self.dataAgora.replace('_', ' ') + '</span> &nbsp;&nbsp;&nbsp;&nbsp; ')
		arquivoHtml = arquivoHtml.replace('id="apagar_link" value="link1"', 'id=apagar_link value="' + slugify(self.nomePesquisa) + '_' + self.dataAgora + '"')

		return arquivoHtml

	def adicionarDistribution(self):
		if self.criterio == "5":
			return self.arquivoHtml.replace("!--DIST", "").replace("DIST-->", f"><form id=dist action='../../cgi-bin/distribution.py' method=POST><input type=hidden name=html id=html_dist value='{self.caminhoCompletoHtml}'><input type=hidden name=coluna id=coluna_dist><input id=expressao_dist type=hidden name=expressao><input id=corpus_dist type=hidden name=corpus><input id=combination_dist type=hidden name=combination></form>")
		return self.arquivoHtml

	def adicionarExecutarScript(self):
		arquivoHtml = self.arquivoHtml.split("<!--script-->")
		arquivoHtml[0] += f"<form method=POST action=\"../../cgi-bin/inquerito.py?action=script&executar=sim\" target=\"_blank\">"
		arquivoHtml[0] += f"<input type=hidden name=nome_interrogatorio value=\"{cgi.escape(self.nomePesquisa)}\"><input type=hidden name=occ value=\"{self.numeroOcorrencias}\"><input type=hidden name=link_interrogatorio value=\"{self.caminhoCompletoHtml}\"><input type=hidden name=conllu value=\"{self.conllu}\">"
		arquivoHtml[0] += "<input type=text name=script list=lista required><datalist id=lista>"

		if not os.path.isdir('../interrogar-ud/scripts/'):
			os.mkdir('../interrogar-ud/scripts')
		for item in os.listdir('../interrogar-ud/scripts/'):
			if '.py' in item and not item in ["estrutura_dados.py", "estrutura_ud.py", "MODELO-UD.py", "MODELO.py"]:
				arquivoHtml[0] += f'<option value=\"{item}\">{item}</option>'
		
		arquivoHtml[0] += '</datalist> <input type="submit" value="Executar"></form>'

		return "".join(arquivoHtml)

	def adicionarNumeroHtml(self, i, ocorrencia):
		return f'<p>{str(i+1)}/{self.numeroOcorrencias}</p>'

	def adicionarSentIdHtml(self, i, ocorrencia):
		if ocorrencia['resultadoEstruturado'].sent_id:
			return f'''<p><input class=cb id=checkbox_{str(i+1)} style="margin-left:0px;" title="Selecionar sentença para filtragem" type=checkbox> {ocorrencia['resultadoEstruturado'].sent_id}</p>'''
		return ""

	def adicionarTextHtml(self, i, ocorrencia):
		return f"<p><span id=text_{str(i+1)}>{ocorrencia['resultadoAnotado'].text.replace('/BOLD', '</b>').replace('@BOLD', '<b>').replace('@YELLOW/', '<font color=' + tabela['yellow'] + '>').replace('@PURPLE/', '<font color=' + tabela['purple'] + '>').replace('@BLUE/', '<font color=' + tabela['blue'] + '>').replace('@RED/', '<font color=' + tabela['red'] + '>').replace('@CYAN/', '<font color=' + tabela['cyan'] + '>').replace('/FONT', '</font>')}</span></p>"

	def adicionarFormInquerito(self, i, ocorrencia):
		return f"<form action=\"../../cgi-bin/inquerito.py?conllu={self.conllu}\" target=\"_blank\" method=POST id=form_{str(i+1)}><input type=hidden name=sentid value=\"{ocorrencia['resultadoEstruturado'].sent_id}\"><input type=hidden name=occ value=\"{self.numeroOcorrencias}\"><input type=hidden name=textheader value=\"{ocorrencia['resultadoEstruturado'].text}\"><input type=hidden name=nome_interrogatorio value=\"{cgi.escape(self.nomePesquisa)}\"><input type=hidden name=link_interrogatorio value=\"{self.caminhoCompletoHtml}\"></form>"

	def adicionarOpcaoFiltrar(self, i, ocorrencia):
		return f"<a style=\"cursor:pointer\" onclick='filtraragora(\"{str(i+1)}\")'>Separar sentença</a>"

	def adicionarFormEOpcaoUDPipe(self, i, ocorrencia):
		return f"<form action=\"../../cgi-bin/udpipe.py?conllu={self.conllu}\" target=\"_blank\" method=POST id=udpipe_{str(i+1)}><input type=hidden name=textheader value=\"{ocorrencia['resultadoEstruturado'].text}\"></form><a style=\"cursor:pointer\" onclick='anotarudpipe(\"udpipe_{str(i+1)}\")'>Anotar no UDPipe</a>"

	def adicionarFormEOpcaoTree(self, i, ocorrencia):
		return f"<form action=\"../../cgi-bin/draw_tree.py?conllu={self.conllu}\" target=\"_blank\" method=POST id=tree_{str(i+1)}><input type=hidden name=sent_id value=\"{ocorrencia['resultadoEstruturado'].sent_id}\"><input type=hidden name=text value=\"{ocorrencia['resultadoEstruturado'].text}\"></form><a style=\"cursor:pointer\" onclick='drawtree(\"tree_{str(i+1)}\")'>Visualizar árvore</a>"

	def adicionarAnotacaoHtml(self, i, ocorrencia):
		return f"<pre id=div_{str(i+1)} style=\"display:none\">{ocorrencia['resultadoAnotado'].to_str().replace('/BOLD', '</b>').replace('@BOLD', '<b>').replace('@YELLOW/', '<font color=' + tabela['yellow'] + '>').replace('@PURPLE/', '<font color=' + tabela['purple'] + '>').replace('@BLUE/', '<font color=' + tabela['blue'] + '>').replace('@RED/', '<font color=' + tabela['red'] + '>').replace('@CYAN/', '<font color=' + tabela['cyan'] + '>').replace('/FONT', '</font>')}</pre>"

	def montarHtml(self):
		with open("../interrogar-ud/resultados/link1.html", "r") as f:
			self.arquivoHtml = f.read()
			self.arquivoHtml = self.arquivoHtml.replace('../../cgi-bin/filtrar.cgi', '../../cgi-bin/filtrar.cgi?html=' + slugify(self.nomePesquisa) + '_' + self.dataAgora + '&udoriginal=' + self.conllu)
			self.arquivoHtml = self.arquivoHtml.replace('../../cgi-bin/conllu.cgi', '../../cgi-bin/conllu.cgi?html=../interrogar-ud/resultados/' + slugify(self.nomePesquisa) + '_' + self.dataAgora + '.html')
		self.corpus = estrutura_ud.Corpus(recursivo=False)
		self.corpus.load(self.caminhoCompletoConllu)

		self.arquivoHtml = self.adicionarHeader()
		self.arquivoHtml = self.adicionarDistribution()
		self.arquivoHtml = self.adicionarExecutarScript()

		self.arquivoHtml = self.arquivoHtml.split('<!--SPLIT-->')
		for i, ocorrencia in enumerate(self.dicionarioOcorrencias):
			self.arquivoHtml[0] += '<div class=container>\n'
			self.arquivoHtml[0] += self.adicionarNumeroHtml(i, ocorrencia) + '\n'
			self.arquivoHtml[0] += self.adicionarSentIdHtml(i, ocorrencia) + '\n'
			self.arquivoHtml[0] += self.adicionarTextHtml(i, ocorrencia) + '\n'
			self.arquivoHtml[0] += adicionarBotoesEContextoHtml(self.caminhoCompletoConllu, i, ocorrencia, self.corpus) + '\n'
			self.arquivoHtml[0] += f"<span style=\"display:none; padding-left:20px;\" id=\"optdiv_{str(i+1)}\">"
			self.arquivoHtml[0] += self.adicionarFormInquerito(i, ocorrencia)
			self.arquivoHtml[0] += self.adicionarOpcaoFiltrar(i, ocorrencia)
			self.arquivoHtml[0] += '<br>'
			self.arquivoHtml[0] += self.adicionarFormEOpcaoUDPipe(i, ocorrencia)
			self.arquivoHtml[0] += '<br>'
			self.arquivoHtml[0] += self.adicionarFormEOpcaoTree(i, ocorrencia)
			self.arquivoHtml[0] += '</p></span>\n'
			self.arquivoHtml[0] += self.adicionarAnotacaoHtml(i, ocorrencia) + '\n'
			self.arquivoHtml[0] += '</div>\n'

		return "".join(self.arquivoHtml)


def adicionarBotoesEContextoHtml(caminhoCompletoConllu, i, ocorrencia, corpus):

	def adicionarContexto(caminhoCompletoConllu, i, ocorrencia, corpus):
		contextoEsquerda = ""
		contextoDireita = ""

		if ocorrencia['resultadoEstruturado'].sent_id:
			if '-' in ocorrencia['resultadoEstruturado'].sent_id and re.search(r'^\d+$', ocorrencia['resultadoEstruturado'].sent_id.rsplit('-', 1)[1]):
				contextoEsquerda = corpus.sentences[ocorrencia['resultadoEstruturado'].sent_id.rsplit('-', 1)[0] + '-' + str(int(ocorrencia['resultadoEstruturado'].sent_id.rsplit('-', 1)[1]) - 1)].text if ocorrencia['resultadoEstruturado'].sent_id.rsplit('-', 1)[0] + '-' + str(int(ocorrencia['resultadoEstruturado'].sent_id.rsplit('-', 1)[1]) - 1) in corpus.sentences else ""
				contextoDireita = corpus.sentences[ocorrencia['resultadoEstruturado'].sent_id.rsplit('-', 1)[0] + '-' + str(int(ocorrencia['resultadoEstruturado'].sent_id.rsplit('-', 1)[1]) + 1)].text if ocorrencia['resultadoEstruturado'].sent_id.rsplit('-', 1)[0] + '-' + str(int(ocorrencia['resultadoEstruturado'].sent_id.rsplit('-', 1)[1]) + 1) in corpus.sentences else ""

			elif re.search(r'^\d+$', ocorrencia['resultadoEstruturado'].sent_id):
				contextoEsquerda = corpus.sentences[str(int(ocorrencia['resultadoEstruturado'].sent_id) - 1)].text if str(int(ocorrencia['resultadoEstruturado'].sent_id) - 1) in corpus.sentences else ""
				contextoDireita = corpus.sentences[str(int(ocorrencia['resultadoEstruturado'].sent_id) + 1)].text if str(int(ocorrencia['resultadoEstruturado'].sent_id) + 1) in corpus.sentences else ""

		elif ocorrencia['resultadoEstruturado'].id:
			if re.search(r'^\d+$', ocorrencia['resultadoEstruturado'].id):
				contextoEsquerda = corpus.sentences[str(int(ocorrencia['resultadoEstruturado'].id) - 1)].text if str(int(ocorrencia['resultadoEstruturado'].id) - 1) in corpus.sentences else ""
				contextoDireita = corpus.sentences[str(int(ocorrencia['resultadoEstruturado'].id) + 1)].text if str(int(ocorrencia['resultadoEstruturado'].id) + 1) in corpus.sentences else ""

		return f"<p id=divcontexto_{str(i+1)} style=\"display:none\">{contextoEsquerda} {ocorrencia['resultadoAnotado'].text.replace('/BOLD','</b>').replace('@BOLD','<b>').replace('@YELLOW/', '<font color=' + tabela['yellow'] + '>').replace('@PURPLE/', '<font color=' + tabela['purple'] + '>').replace('@BLUE/', '<font color=' + tabela['blue'] + '>').replace('@RED/', '<font color=' + tabela['red'] + '>').replace('@CYAN/', '<font color=' + tabela['cyan'] + '>').replace('/FONT', '</font>')} {contextoDireita}</p>"

	if ((ocorrencia['resultadoEstruturado'].sent_id and ('-' in ocorrencia['resultadoEstruturado'].sent_id or re.search(r'^\d+$', ocorrencia['resultadoEstruturado'].sent_id))) or ocorrencia['resultadoEstruturado'].id) and ocorrencia['resultadoEstruturado'].text:
		return f"<p><input id=contexto_{str(i+1)} value=\"Mostrar contexto\" onclick=\"contexto('divcontexto_{str(i+1)}', 'contexto_{str(i+1)}')\" style=\"margin-left:0px\" type=button> <input id=mostrar_{str(i+1)} class=anotacao value=\"Mostrar anotação\" onclick=\"mostrar('div_{str(i+1)}', 'mostrar_{str(i+1)}')\" style=\"margin-left:0px\" type=button> <input id=opt_{str(i+1)} class=opt value=\"Mostrar opções\" onclick=\"mostraropt('optdiv_{str(i+1)}', 'opt_{str(i+1)}')\" style=\"margin-left:0px\" type=button> <input type=button value=\"Abrir inquérito\" onclick='inquerito(\"form_{str(i+1)}\")'></p>" + adicionarContexto(caminhoCompletoConllu, i, ocorrencia, corpus)

	return f"<p><input id=mostrar_{str(i+1)} class=anotacao value=\"Mostrar anotação\" onclick=\"mostrar('div_{str(i+1)}', 'mostrar_{str(i+1)}')\" style=\"margin-left:0px\" type=button> <input id=opt_{str(i+1)} class=opt value=\"Mostrar opções\" onclick=\"mostraropt('optdiv_{str(i+1)}', 'opt_{str(i+1)}')\" style=\"margin-left:0px\" type=button> <input type=button value=\"Abrir inquérito\" onclick='inquerito(\"form_{str(i+1)}\")'></p>"


if __name__ == "__main__":
	main()