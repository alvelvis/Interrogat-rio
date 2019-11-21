#!/usr/bin/python3
# -*- coding: UTF-8 -*-

fastSearch = ['teste', 'Busca rápida']

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
from functions import tabela, prettyDate, encodeUrl
import html as web
import time
import sys
import functions

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
		criteriosBusca = [x + "<br>[<a href='#criterio_-1'>Voltar ao menu</a>]" for x in criteriosBusca if x.strip()]

	paginaHTML[0] += "\n".join(["<div class=container-lr id=criterio_{0}>{1}</div>".format(i-1, criterio) for i, criterio in enumerate(criteriosBusca)])

	paginaHTML = "".join(paginaHTML)
	paginaHTML = paginaHTML.split("<!--selectpicker-->")[0] + "\n".join(arquivosCONLLU) + paginaHTML.split("<!--selectpicker-->")[1]

	refazerPesquisa = cgi.FieldStorage()['params'].value.replace("'", '"') if 'params' in cgi.FieldStorage() else ""
	refazerCorpus = cgi.FieldStorage()['corpus'].value if 'corpus' in cgi.FieldStorage() else ""
	paginaHTML = paginaHTML.replace('id="pesquisa"', f'''id="pesquisa" value='{refazerPesquisa}\'''').replace(f"value='{refazerCorpus}'", f"value='{refazerCorpus}' selected")
	if 'save' in cgi.FieldStorage():
		paginaHTML = paginaHTML.replace('checked><div onclick="$(\'.toggleRapida\')', '><div onclick="$(\'.toggleRapida\')').replace('><div onclick="$(\'.toggleSalvar\')', 'checked><div onclick="$(\'.toggleSalvar\')"')
	if 'go' in cgi.FieldStorage():
		paginaHTML = paginaHTML.split("</body>")[0] + '<script>$("body").ready(function(){$("#enviar").click()})</script>' + "</body>" + paginaHTML.split("</body>")[1]
	print(paginaHTML)


def sendPOSTInterrogar():
	criterio, parametros, conllu, nomePesquisa, script, sentLimit = definirVariaveisDePesquisa(cgi.FieldStorage())

	caminhoCompletoConllu = "../interrogar-ud/conllu/" + conllu
	dataAgora = str(datetime.now()).replace(' ', '_').split('.')[0]
	caminhoCompletoHtml = '../interrogar-ud/resultados/' + slugify(nomePesquisa) + '_' + dataAgora + '.html'

	if nomePesquisa and nomePesquisa not in fastSearch:
		with open(f"../interrogar-ud/inProgress/{conllu} {criterio} {parametros} {dataAgora}.inProgress", 'w') as f:
			f.write("")

	dicionarioOcorrencias, numeroOcorrencias, casosOcorrencias = realizarBusca(caminhoCompletoConllu, int(criterio), parametros, script, sentLimit)

	start = time.time()
	arquivoHtml = paginaHtml(caminhoCompletoConllu, caminhoCompletoHtml, nomePesquisa, dataAgora, conllu, criterio, parametros, dicionarioOcorrencias, numeroOcorrencias, casosOcorrencias).montarHtml()
	print("<br>montarHtml: " + str(time.time() - start))

	if nomePesquisa and nomePesquisa not in fastSearch:
		os.remove("../interrogar-ud/inProgress/{0} {1} {2} {3}.inProgress".format(conllu, criterio, parametros, dataAgora))

	#Printar sem as funções mais importantes caso seja Busca rápida
	if nomePesquisa in fastSearch:
		print(re.sub(r'<button.*?filtrar.*?\n.*?</button>', '', re.sub(r'<button.*?conllu.*?\n.*?</button>', '', re.sub(r'<input.*?checkbox.*?>', '', arquivoHtml))).replace("../../", "../").replace("Correção em lote", "").replace("Selecionar todas as sentenças", "").replace("Deselecionar todas as sentenças", "").replace('Selecionar múltiplas sentenças', '').replace("<br>\n<br>", "").replace('<div class="content"><br>', '<div class="content"><a href="#" onclick="document.location.href = $(\'.refazerPesquisa\').attr(\'href\') + \'&save=True&go=True\';">Salve a busca</a> para liberar mais funções.<br>'))
		exit()

	with open(caminhoCompletoHtml, "w") as f:
		f.write(arquivoHtml)

	queries = ["\t".join([caminhoCompletoHtml, nomePesquisa, numeroOcorrencias, criterio, parametros, conllu, dataAgora])]

	with open('../interrogar-ud/queries.txt', 'r') as f:
		queries.extend(f.read().splitlines())

	open('../interrogar-ud/queries.txt', 'w').write("\n".join(queries))

	print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body onload="redirect()"><script>function redirect() { window.location = "'+caminhoCompletoHtml+'" }</script></body>')


def definirVariaveisDePesquisa(form):
	if 'scriptQueryFile' and form['scriptQueryFile'].value:
		with open('../cgi-bin/queryScript.py', 'wb') as f:
			f.write(form['scriptQueryFile'].file.read())
		script = True
	else:
		script = False

	pesquisa = form['pesquisa'].value.strip()
	if re.search(r'^\d+$', pesquisa.split(' ')[0]):
		criterio = pesquisa.split(' ')[0]
		parametros = pesquisa.split(' ', 1)[1]
	else:
		criterio = '1'
		parametros = pesquisa

	conllu = form['conllu'].value
	nomePesquisa = 'Busca rápida' if form['meth'].value != 'salvar' else form['nome'].value
	sentLimit = int(form['sentLimit'].value) if 'sentLimit' in form and form['meth'].value == 'salvar' else 0

	return criterio, parametros, conllu, nomePesquisa, script, sentLimit


def realizarBusca(caminhoCompletoConllu, criterio, parametros, script, sentLimit):
	if not script:
		resultadosBusca = interrogar_UD.main(caminhoCompletoConllu, criterio, parametros, sentLimit)
	else:
		with open("../cgi-bin/queryScript.py", 'r') as f:
			scriptFile = f.read().replace("<!--corpus-->", caminhoCompletoConllu)
		with open("../cgi-bin/queryScript.py", "w") as f:
			f.write(scriptFile)
		import queryScript
		resultadosBusca = queryScript.getResultadosBusca()

	dicionarioOcorrencias = resultadosBusca['output']
	numeroOcorrencias = str(len(resultadosBusca['output']))
	casosOcorrencias = resultadosBusca['casos']

	return dicionarioOcorrencias, numeroOcorrencias, casosOcorrencias


class paginaHtml():

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
		casos = f"<br>Casos: {str(self.casosOcorrencias)}" if self.casosOcorrencias else ""
		arquivoHtml = arquivoHtml.replace('<h1><span id="combination">link de pesquisa 1</span> (203)</h1>', '<h1><a style="color:black; max-width: 40vw; word-wrap: break-word;" id=titulo><span id=combination>' + cgi.escape(self.nomePesquisa) + '</span> (' + self.numeroOcorrencias + ')</a></h1>' + casos)

		with open ('../interrogar-ud/criterios.txt', 'r') as f:
			criterios = f.read().split('!@#')
		criterios = [x for x in criterios if x.strip()]
		
		refazerPesquisa = '<br><a class="refazerPesquisa" href="../../cgi-bin/interrogar.cgi?corpus=' + self.conllu + '&params=' + self.criterio + ' ' + encodeUrl(self.parametros.replace('"', "'")) + '">Refazer busca</a>'
		arquivoHtml = arquivoHtml.replace('<p>critério y#z#k&nbsp;&nbsp;&nbsp; arquivo_UD&nbsp;&nbsp;&nbsp; <span id="data">data</span>&nbsp;&nbsp;&nbsp;', '<p><div class=tooltip style="max-width: 60vw; word-wrap: break-word;"><span id=expressao>' + self.criterio + ' ' + cgi.escape(self.parametros) + '</span><span class=tooltiptext>' + criterios[int(self.criterio)+1].split('<h4>')[0] + '</span></div>' + refazerPesquisa + f'<br><br><a href="../../interrogar-ud/conllu/{self.conllu}" title="Baixar corpus" download><span id=corpus>' + self.conllu + '</span></a><br><span id=data><small>' + prettyDate(self.dataAgora.replace('_', ' ')).beautifyDateDMAH() + '</small></span>')
		arquivoHtml = arquivoHtml.replace('id="apagar_link" value="link1"', 'id=apagar_link value="' + slugify(self.nomePesquisa) + '_' + self.dataAgora + '"')

		return arquivoHtml

	def adicionarDistribution(self):
		if self.criterio == "5":
			if self.nomePesquisa not in fastSearch:
				return self.arquivoHtml.replace("!--DIST", "").replace("DIST-->", f"><form id=dist target='_blank' action='../../cgi-bin/distribution.py' method=POST><input type=hidden name=html id=html_dist value='{self.caminhoCompletoHtml}'><input type=hidden name=coluna id=coluna_dist><input id=expressao_dist type=hidden name=expressao><input id=corpus_dist type=hidden name=corpus><input id=combination_dist type=hidden name=combination></form>")
			return self.arquivoHtml.replace("!--DIST", "").replace("DIST-->", "><form id=dist target='_blank' action='../../cgi-bin/distribution.py' method=POST><input type=hidden name=notSaved id=html_dist value='{0}'><input type=hidden name=coluna id=coluna_dist><input id=expressao_dist type=hidden name=expressao><input id=corpus_dist type=hidden name=corpus><input id=combination_dist type=hidden name=combination></form>".format(self.parametros.replace("'", '"')))
			#return self.arquivoHtml.replace("DIST-->", 'DIST--><a href="#" onclick="document.location.href = $(\'.refazerPesquisa\').attr(\'href\') + \'&save=True\';">Salve a busca</a> para visualizar a distribuição das palavras em negrito.')
		return self.arquivoHtml

	def adicionarExecutarScript(self):
		arquivoHtml = self.arquivoHtml.split("<!--script-->")
		arquivoHtml[0] += f"<input type=hidden name=nome_interrogatorio value=\"{cgi.escape(self.nomePesquisa)}\"><input type=hidden name=occ value=\"{self.numeroOcorrencias}\"><input type=hidden name=link_interrogatorio value=\"{self.caminhoCompletoHtml}\"><input type=hidden name=conllu value=\"{self.conllu}\">"

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
		formInquerito = f"<form action=\"../../cgi-bin/inquerito.py?conllu={self.conllu}\" target=\"_blank\" method=POST id=form_{str(i+1)}><input type=hidden name=sentid value=\"{ocorrencia['resultadoEstruturado'].sent_id}\"><input type=hidden name=occ value=\"{self.numeroOcorrencias}\"><input type=hidden name=textheader value=\"{ocorrencia['resultadoEstruturado'].text}\"><input type=hidden name=nome_interrogatorio value=\"{cgi.escape(self.nomePesquisa)}\"><input type=hidden name=link_interrogatorio value=\"{self.caminhoCompletoHtml}\">"
		if "@BOLD" in ocorrencia['resultadoAnotado'].to_str():
			formInquerito += f"<input type=hidden name=tokenId value=\"" + "".join([functions.cleanEstruturaUD(x.id) for x in ocorrencia['resultadoAnotado'].tokens if '@BOLD' in x.to_str()]) + "\">"
		return formInquerito + "</form>"

	def adicionarOpcaoFiltrar(self, i, ocorrencia):
		return f"<!--a style=\"cursor:pointer\" onclick='filtraragora(\"{str(i+1)}\")'>Separar sentença</a-->"

	def adicionarFormEOpcaoUDPipe(self, i, ocorrencia):
		return f"<form action=\"../../cgi-bin/udpipe.py?conllu={self.conllu}\" target=\"_blank\" method=POST id=udpipe_{str(i+1)}><input type=hidden name=textheader value=\"{ocorrencia['resultadoEstruturado'].text}\"></form><a style=\"cursor:pointer\" onclick='anotarudpipe(\"udpipe_{str(i+1)}\")'>Anotar frase com o UDPipe</a>"

	def adicionarFormEOpcaoTree(self, i, ocorrencia):
		return f"<form action=\"../../cgi-bin/draw_tree.py?conllu={self.conllu}\" target=\"_blank\" method=POST id=tree_{str(i+1)}><input type=hidden name=sent_id value=\"{ocorrencia['resultadoEstruturado'].sent_id}\"><input type=hidden name=text value=\"{ocorrencia['resultadoEstruturado'].text}\"></form><a style=\"cursor:pointer\" onclick='drawtree(\"tree_{str(i+1)}\")'>Visualizar árvore de dependências</a>"

	def adicionarAnotacaoHtml(self, i, ocorrencia):
		return f"<pre id=div_{str(i+1)} style=\"display:none\">{ocorrencia['resultadoAnotado'].to_str()}"#.replace('/BOLD', '</b>').replace('@BOLD', '<b>').replace('@YELLOW/', '<font color=' + tabela['yellow'] + '>').replace('@PURPLE/', '<font color=' + tabela['purple'] + '>').replace('@BLUE/', '<font color=' + tabela['blue'] + '>').replace('@RED/', '<font color=' + tabela['red'] + '>').replace('@CYAN/', '<font color=' + tabela['cyan'] + '>').replace('/FONT', '</font>')}</pre>"

	def montarHtml(self):
		with open("../interrogar-ud/resultados/link1.html", "r") as f:
			self.arquivoHtml = f.read()
			self.arquivoHtml = self.arquivoHtml.replace('../../cgi-bin/filtrar.cgi', '../../cgi-bin/filtrar.cgi?html=' + slugify(self.nomePesquisa) + '_' + self.dataAgora + '&udoriginal=' + self.conllu)
			self.arquivoHtml = self.arquivoHtml.replace('../../cgi-bin/conllu.cgi', '../../cgi-bin/conllu.cgi?html=../interrogar-ud/resultados/' + slugify(self.nomePesquisa) + '_' + self.dataAgora + '.html')

		self.arquivoHtml = self.adicionarHeader()
		self.arquivoHtml = self.adicionarDistribution()
		self.arquivoHtml = self.adicionarExecutarScript()

		t1 = 0
		t2 = 0
		t3 = 0
		t4 = 0
		t5 = 0
		t6 = 0
		t7 = 0
		t8 = 0
		t9 = 0
		self.arquivoHtml = self.arquivoHtml.split('<!--SPLIT-->')
		for i, ocorrencia in enumerate(self.dicionarioOcorrencias):
			self.arquivoHtml[0] += '<div class=container>\n'
			t = time.time()
			self.arquivoHtml[0] += self.adicionarNumeroHtml(i, ocorrencia) + '\n'
			t1 += time.time() - t
			t = time.time()
			self.arquivoHtml[0] += self.adicionarSentIdHtml(i, ocorrencia) + '\n'
			t2 += time.time() - t
			t = time.time()
			self.arquivoHtml[0] += self.adicionarTextHtml(i, ocorrencia) + '\n'
			t3 += time.time() - t
			t = time.time()
			self.arquivoHtml[0] += adicionarBotoesEContextoHtml(self.caminhoCompletoConllu, i, ocorrencia, self.conllu) + '\n'
			t4 += time.time() - t
			t = time.time()
			self.arquivoHtml[0] += f"<span style=\"display:none; padding-left:20px;\" id=\"optdiv_{str(i+1)}\">"
			self.arquivoHtml[0] += self.adicionarFormInquerito(i, ocorrencia)
			t5 += time.time() - t
			t = time.time()
			if self.nomePesquisa not in fastSearch: self.arquivoHtml[0] += self.adicionarOpcaoFiltrar(i, ocorrencia)
			t6 += time.time() - t
			t = time.time()
			self.arquivoHtml[0] += '<br>'
			self.arquivoHtml[0] += self.adicionarFormEOpcaoUDPipe(i, ocorrencia)
			t7 += time.time() - t
			t = time.time()
			self.arquivoHtml[0] += '<br>'
			self.arquivoHtml[0] += self.adicionarFormEOpcaoTree(i, ocorrencia)
			t8 += time.time() - t
			t = time.time()
			self.arquivoHtml[0] += '</p></span>\n'
			self.arquivoHtml[0] += self.adicionarAnotacaoHtml(i, ocorrencia) + '\n'
			t9 += time.time() - t
			self.arquivoHtml[0] += '</div>\n'
		print(f"<br>t1: {t1}")
		print(f"<br>t2: {t2}")
		print(f"<br>t3: {t3}")
		print(f"<br>t4: {t4}")
		print(f"<br>t5: {t5}")
		print(f"<br>t6: {t6}")
		print(f"<br>t7: {t7}")
		print(f"<br>t8: {t8}")
		print(f"<br>t9: {t9}")

		return "".join(self.arquivoHtml)


def adicionarBotoesEContextoHtml(caminhoCompletoConllu, i, ocorrencia, corpus):

	if ((ocorrencia['resultadoEstruturado'].sent_id and ('-' in ocorrencia['resultadoEstruturado'].sent_id or re.search(r'^\d+$', ocorrencia['resultadoEstruturado'].sent_id))) or ocorrencia['resultadoEstruturado'].id) and ocorrencia['resultadoEstruturado'].text:
		return f"<p><input id=contexto_{str(i+1)} value=\"Mostrar contexto\" onclick=\"contexto('{ocorrencia['resultadoEstruturado'].sent_id}', '{ocorrencia['resultadoEstruturado'].id}', '{corpus}')\" style=\"margin-left:0px\" type=button> <input id=mostrar_{str(i+1)} class=anotacao value=\"Mostrar anotação\" onclick=\"mostrar('div_{str(i+1)}', 'mostrar_{str(i+1)}')\" style=\"margin-left:0px\" type=button> <input id=opt_{str(i+1)} class=opt value=\"Mostrar opções\" onclick=\"mostraropt('optdiv_{str(i+1)}', 'opt_{str(i+1)}')\" style=\"margin-left:0px\" type=button> <input class=\"abrirInquerito\" type=button value=\"Abrir inquérito\" onclick='inquerito(\"form_{str(i+1)}\")'></p>"

	return f"<p><input id=mostrar_{str(i+1)} class=anotacao value=\"Mostrar anotação\" onclick=\"mostrar('div_{str(i+1)}', 'mostrar_{str(i+1)}')\" style=\"margin-left:0px\" type=button> <input id=opt_{str(i+1)} class=opt value=\"Mostrar opções\" onclick=\"mostraropt('optdiv_{str(i+1)}', 'opt_{str(i+1)}')\" style=\"margin-left:0px\" type=button> <input type=button value=\"Abrir inquérito\" onclick='inquerito(\"form_{str(i+1)}\")'></p>"


if __name__ == "__main__":
	main()
