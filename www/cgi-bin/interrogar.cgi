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
import json
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
		criteriosBusca = [("[<a href='#' class='toggleCriteria' criterio='-1'>Voltar</a>]<br>" if i != 0 else "") + x for i, x in enumerate(criteriosBusca) if x.strip()]

	paginaHTML[0] += "\n".join(["<div class='container-lr criterio' {2} id=criterio_{0}>{1}</div>".format(i-1, criterio, " style='display:none'" if i-1 != -1 else "") for i, criterio in enumerate(criteriosBusca)])

	paginaHTML = "".join(paginaHTML)
	paginaHTML = paginaHTML.split("<!--selectpicker-->")[0] + "<option disabled selected value> -- escolha um corpus -- </option>" + "\n".join(arquivosCONLLU) + paginaHTML.split("<!--selectpicker-->")[1]

	refazerPesquisa = cgi.FieldStorage()['params'].value.replace("'", '"') if 'params' in cgi.FieldStorage() else ""
	refazerCorpus = cgi.FieldStorage()['corpus'].value if 'corpus' in cgi.FieldStorage() else ""
	paginaHTML = paginaHTML.replace('id="pesquisa"', f'''id="pesquisa" value='{refazerPesquisa}\'''').replace(f"value='{refazerCorpus}'", f"value='{refazerCorpus}' selected")
	if 'save' in cgi.FieldStorage():
		paginaHTML = paginaHTML.replace('checked><div onclick="$(\'.toggleRapida\')', '><div onclick="$(\'.toggleRapida\')').replace('><div onclick="$(\'.toggleSalvar\')', 'checked><div onclick="$(\'.toggleSalvar\')"')
	if 'go' in cgi.FieldStorage():
		paginaHTML = paginaHTML.split("</body>")[0] + '<script>$("body").ready(function(){$("#enviar").click()})</script>' + "</body>" + paginaHTML.split("</body>")[1]
	print(paginaHTML)


def sendPOSTInterrogar():

	criterio, parametros, conllu, nomePesquisa, script = definirVariaveisDePesquisa(cgi.FieldStorage())

	caminhoCompletoConllu = "../interrogar-ud/conllu/" + conllu
	dataAgora = str(datetime.now()).replace(' ', '_').split('.')[0]
	caminhoCompletoHtml = '../interrogar-ud/resultados/' + slugify(nomePesquisa) + '_' + dataAgora + '.html'

	if nomePesquisa and nomePesquisa not in fastSearch:
		with open(f"../interrogar-ud/inProgress/{conllu} {criterio} {parametros} {dataAgora}.inProgress", 'w') as f:
			try:
				f.write("")
			except:
				pass

	numeroOcorrencias, casosOcorrencias = realizarBusca(conllu, caminhoCompletoConllu, int(criterio), parametros, script)

	arquivoHtml = paginaHtml(caminhoCompletoConllu, caminhoCompletoHtml, nomePesquisa, dataAgora, conllu, criterio, parametros, numeroOcorrencias, casosOcorrencias, script).montarHtml()

	if nomePesquisa and nomePesquisa not in fastSearch:
		os.remove("../interrogar-ud/inProgress/{0} {1} {2} {3}.inProgress".format(conllu, criterio, parametros, dataAgora))

	#Printar sem as funções mais importantes caso seja Busca rápida
	if nomePesquisa in fastSearch:
		print(re.sub(r'<button.*?filtrar.*?\n.*?</button>', '', re.sub(r'<button.*?conllu.*?\n.*?</button>', '', re.sub(r'<input.*?checkbox.*?>', '', arquivoHtml))).replace("../../", "../").replace("<br>\n<br>", "").replace(')</a></h3>', ')</a></h3><span style="background-color:yellow;">Você deseja <a href="#" onmouseover="$(this).css(\'text-decoration\', \'underline\');" onmouseleave="$(this).css(\'text-decoration\', \'none\');" title="Para realizar filtros na página, é preciso salvar esta busca; clique aqui para salvar" style="color:blue" onclick="document.location.href = $(\'.refazerPesquisa\').attr(\'href\') + \'&save=True&go=True\';">salvar esta busca</a>?</span><br>').replace('Selecionar múltiplas sentenças', '').replace('Deselecionar todas as sentenças', '').replace('Selecionar todas as sentenças', ''))
		exit()

	with open(caminhoCompletoHtml, "w") as f:
		f.write(arquivoHtml)

	queries = ["\t".join([caminhoCompletoHtml, nomePesquisa, numeroOcorrencias, criterio, parametros, conllu, dataAgora])]

	if not os.path.isfile("../interrogar-ud/queries.txt"):
		with open("../interrogar-ud/queries.txt", "w") as f:
			f.write("")
	with open('../interrogar-ud/queries.txt', 'r') as f:
		queries.extend(f.read().splitlines())

	open('../interrogar-ud/queries.txt', 'w').write("\n".join(queries))

	print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body onload="redirect()"><script>function redirect() { window.location = "'+caminhoCompletoHtml+'" }</script></body>')


def definirVariaveisDePesquisa(form):
	if 'scriptQueryFile' in form and form['scriptQueryFile'].value:
		if not os.path.isdir('../cgi-bin/scripts'):
			os.mkdir('../cgi-bin/scripts')
		with open('../cgi-bin/scripts/' + form['scriptQueryFile'].filename, 'wb') as f:
			f.write(form['scriptQueryFile'].file.read())
		os.system("cp '../cgi-bin/scripts/" + form['scriptQueryFile'].filename + "' ../cgi-bin/queryScript.py")
		script = form['scriptQueryFile'].filename
		parametros = form['scriptQueryFile'].filename
	else:
		script = False

	pesquisa = form['pesquisa'].value.strip()
	if re.search(r'^\d+$', pesquisa.split(' ')[0]):
		criterio = pesquisa.split(' ')[0]
		parametros = pesquisa.split(' ', 1)[1]
	elif any(x in pesquisa for x in [' == ', ' = ', ' != ', ' !== ', ' === ']):
		criterio = '5'
		parametros = pesquisa
	else:
		criterio = '1'
		parametros = pesquisa

	conllu = form['conllu'].value
	nomePesquisa = 'Busca rápida' if form['meth'].value != 'salvar' else form['nome'].value
	#sentLimit = int(form['sentLimit'].value) if 'sentLimit' in form and form['meth'].value == 'salvar' else 0

	return criterio, parametros, conllu, nomePesquisa, script


def realizarBusca(conllu, caminhoCompletoConllu, criterio, parametros, script=""):
	if not script:
		resultadosBusca = interrogar_UD.main(caminhoCompletoConllu, criterio, parametros, fastSearch=True)
	else:
		with open("../cgi-bin/queryScript.py", 'r') as f:
			scriptFile = f.read().replace("<!--corpus-->", caminhoCompletoConllu)
		with open("../cgi-bin/queryScript.py", "w") as f:
			f.write(scriptFile)
		import queryScript
		resultadosBusca = queryScript.getResultadosBusca()

	if not os.path.isdir('../cgi-bin/json'):
		os.mkdir('../cgi-bin/json')
	try:
		with open("../cgi-bin/json/" + slugify(conllu + "_" + parametros + ".json"), "w") as f:
			json.dump(resultadosBusca, f)
	except:
		pass

	numeroOcorrencias = str(len(resultadosBusca['output']))
	casosOcorrencias = resultadosBusca['casos']

	return numeroOcorrencias, casosOcorrencias


class paginaHtml():

	def __init__(self, caminhoCompletoConllu, caminhoCompletoHtml, nomePesquisa, dataAgora, conllu, criterio, parametros, numeroOcorrencias, casosOcorrencias, script):
		self.caminhoCompletoConllu = caminhoCompletoConllu
		self.caminhoCompletoHtml = caminhoCompletoHtml
		self.nomePesquisa = nomePesquisa
		self.dataAgora = dataAgora
		self.conllu = conllu
		self.criterio = criterio
		self.parametros = parametros
		self.numeroOcorrencias = numeroOcorrencias
		self.casosOcorrencias = casosOcorrencias
		self.script = script
	
	def adicionarHeader(self):
		arquivoHtml = self.arquivoHtml.replace('<title>link de pesquisa 1 (203): Interrogatório</title>', '<title>' + cgi.escape(self.nomePesquisa) + ' (' + self.numeroOcorrencias + '): Interrogatório</title>')
		casos = f"<br>Casos: {str(self.casosOcorrencias)}" if self.casosOcorrencias else ""
		arquivoHtml = arquivoHtml.replace('<h3><span id="combination">link de pesquisa 1</span> (203)</h3>', '<h3><a style="color:black; max-width: 40vw; word-wrap: break-word;" id=titulo><span id=combination>' + cgi.escape(self.nomePesquisa) + '</span> (' + self.numeroOcorrencias + ')</a></h3>' + casos)

		with open ('../interrogar-ud/criterios.txt', 'r') as f:
			criterios = f.read().split('!@#')
		criterios = [x for x in criterios if x.strip()]
		
		refazerPesquisa = '<br>Refazer busca</a>'
		arquivoHtml = arquivoHtml.replace('<p>critério y#z#k&nbsp;&nbsp;&nbsp; arquivo_UD&nbsp;&nbsp;&nbsp; <span id="data">data</span>&nbsp;&nbsp;&nbsp;', '<p><!--div class=tooltip style="max-width: 60vw; word-wrap: break-word;"--><a class="refazerPesquisa" title="Refazer busca" href="../../cgi-bin/interrogar.cgi?corpus=' + self.conllu + '&params=' + self.criterio + ' ' + encodeUrl(self.parametros.replace('"', "'")) + '"><span id=expressao>' + self.criterio + ' ' + cgi.escape(self.parametros) + '</span></a><!--span class=tooltiptext>' + criterios[int(self.criterio)+1].split('<h4>')[0] + '</span></div-->' + f'<br><br><a href="../../interrogar-ud/conllu/{self.conllu}" title="Baixar corpus" download><span id=corpus>' + self.conllu + '</span></a><br><span id=data><small>' + prettyDate(self.dataAgora.replace('_', ' ')).beautifyDateDMAH() + '</small></span>')
		arquivoHtml = arquivoHtml.replace('id="apagar_link" value="link1"', 'id=apagar_link value="' + slugify(self.nomePesquisa) + '_' + self.dataAgora + '"')

		return arquivoHtml

	def adicionarDistribution(self):
		if self.criterio == "5":
			if self.nomePesquisa not in fastSearch:
				return self.arquivoHtml.replace("!--DIST", "").replace("DIST-->", "><form id=dist target='_blank' action='../../cgi-bin/distribution.py' method=POST><input type=hidden name=notSaved id=html_dist value='{0}'><input type=hidden name=html id=html_dist value='{1}'><input type=hidden name=coluna id=coluna_dist><input id=expressao_dist type=hidden name=expressao><input id=corpus_dist type=hidden name=corpus><input id=combination_dist type=hidden name=combination><input id=link_dist type=hidden name=link_dist></form>").format(self.parametros.replace("'", '"'), self.caminhoCompletoHtml)
			return self.arquivoHtml.replace("!--DIST", "").replace("DIST-->", "><form id=dist target='_blank' action='../../cgi-bin/distribution.py' method=POST><input type=hidden name=notSaved id=html_dist value='{0}'><input type=hidden name=coluna id=coluna_dist><input id=expressao_dist type=hidden name=expressao><input id=corpus_dist type=hidden name=corpus><input id=combination_dist type=hidden name=combination><input id=link_dist type=hidden name=link_dist></form>".format(self.parametros.replace("'", '"')))
			#return self.arquivoHtml.replace("DIST-->", 'DIST--><a href="#" onclick="document.location.href = $(\'.refazerPesquisa\').attr(\'href\') + \'&save=True\';">Salve a busca</a> para visualizar a distribuição das palavras em negrito.')
		return self.arquivoHtml

	def adicionarExecutarScript(self):
		arquivoHtml = self.arquivoHtml.split("<!--script-->")
		arquivoHtml[0] += f"<input type=hidden name=criterio value=\"{self.criterio}\"><input type=hidden name=parametros value=\'{self.parametros}\'><input type=hidden name=nome_interrogatorio value=\"{cgi.escape(self.nomePesquisa)}\"><input type=hidden name=occ value=\"{self.numeroOcorrencias}\"><input type=hidden name=link_interrogatorio value=\"{self.caminhoCompletoHtml}\"><input type=hidden name=conllu value=\"{self.conllu}\">"

		return "".join(arquivoHtml)

	def montarHtml(self):
		with open("../interrogar-ud/resultados/link1.html", "r") as f:
			self.arquivoHtml = f.read()
			self.arquivoHtml = self.arquivoHtml.replace('../../cgi-bin/filtrar.cgi', '../../cgi-bin/filtrar.cgi?html=' + slugify(self.nomePesquisa) + '_' + self.dataAgora + '&udoriginal=' + self.conllu)
			self.arquivoHtml = self.arquivoHtml.replace('../../cgi-bin/conllu.cgi', '../../cgi-bin/conllu.cgi?html=../interrogar-ud/resultados/' + slugify(self.nomePesquisa) + '_' + self.dataAgora + '.html')

		self.arquivoHtml = self.adicionarHeader()
		if not self.script:
			self.arquivoHtml = self.adicionarDistribution()
			self.arquivoHtml = self.adicionarExecutarScript()
		if self.script:
			self.arquivoHtml = self.arquivoHtml.split("<!--script-->")[0] + f"<input name=queryScript type=hidden value='{slugify(self.script)}'>" + f"<input type=hidden name=conllu value=\"{self.conllu}\">" + f"<input type=hidden name=nome_interrogatorio value=\"{cgi.escape(self.nomePesquisa)}\">" + f"<input type=hidden name=link_interrogatorio value=\"{self.caminhoCompletoHtml}\">" + self.arquivoHtml.split("<!--script-->")[1]

		return self.arquivoHtml


if __name__ == "__main__":
	main()
