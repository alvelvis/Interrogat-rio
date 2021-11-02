#!../.interrogatorio/bin/python3
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
from chardet import detect
import functions

def main():
	if not os.path.isdir("./interrogar-ud/conllu"):
		os.mkdir("./interrogar-ud/conllu")

	sendRequestInterrogar() if os.environ['REQUEST_METHOD'] != "POST" else sendPOSTInterrogar()

def sendRequestInterrogar():
	
	conllu_json = []
	if os.path.isfile('./interrogar-ud/conllu.json'):
		with open("./interrogar-ud/conllu.json") as f:
			conllu_json = json.load(f)

	
	arquivosCONLLU = sorted(["<option value='{0}'>{0}</option>".format(slugify(arquivo)) for arquivo in os.listdir("./interrogar-ud/conllu") if arquivo.endswith(".conllu")])
	corpora_cloud = ['''<nobr><a title='{2}' style="cursor:pointer;" onclick="$('.conllu').val('{0}'); $('.cloud-corpus').css('font-weight', 'normal'); $(this).css('font-weight', 'bold'); $('.cloud-corpus').css('color', ''); $(this).css('color', 'black'); $('.cloud-corpus').css('cursor', 'pointer'); $(this).css('cursor', 'text');" class="cloud-corpus" value='{0}'>{1}</a></nobr>'''.format(
		slugify(arquivo), 
		slugify(arquivo).rsplit(".conllu", 1)[0],
		str(conllu_json[slugify(arquivo)]['n_sent']) + ' sentenças' if slugify(arquivo) in conllu_json else "",
		) for arquivo in sorted(os.listdir("./interrogar-ud/conllu")) if arquivo.endswith(".conllu")]

	
	with open("./interrogar-ud/interrogar_UDnew.html", "r") as f:
		paginaHTML = f.read().split("<!--SPLIT-->")

	with open("./interrogar-ud/criterios.txt", "r") as f:
		criteriosBusca = f.read().split("!@#")
		criteriosBusca = [("[<a href='#' class='toggleCriteria translateHtml' criterio='-1'>Voltar</a>]<br>" if i != 0 else "") + x for i, x in enumerate(criteriosBusca) if x.strip()]

	paginaHTML[0] += "\n".join(["<div class='container-lr criterio' {2} id=criterio_{0}>{1}</div>".format(i-1, criterio, " style='display:none'" if i-1 != -1 else "") for i, criterio in enumerate(criteriosBusca)])

	paginaHTML = "".join(paginaHTML)
	paginaHTML = paginaHTML.split("<!--corpora-cloud-->")[0] + " ".join(corpora_cloud) + paginaHTML.split("<!--corpora-cloud-->")[1]
	paginaHTML = paginaHTML.split("<!--selectpicker-->")[0] + "<option style='display:none' class='translateHtml' disabled selected value> -- escolha um corpus -- </option>" + "\n".join(arquivosCONLLU) + paginaHTML.split("<!--selectpicker-->")[1]

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

	caminhoCompletoConllu = "./interrogar-ud/conllu/" + conllu
	dataAgora = str(datetime.now()).replace(' ', '_').split('.')[0]
	caminhoCompletoHtml = './interrogar-ud/resultados/' + slugify(nomePesquisa) + '_' + dataAgora.replace(':', '_') + '.html'

	if nomePesquisa and nomePesquisa not in fastSearch:
		try:
			with open("./interrogar-ud/inProgress/{}.inProgress".format(f"{conllu} {criterio} {parametros} {dataAgora.replace(':', '_')}"), 'w') as f:
				f.write("")
		except:
			pass

	numeroOcorrencias, casosOcorrencias, fullParameters = realizarBusca(conllu, caminhoCompletoConllu, int(criterio), parametros, script)

	arquivoHtml = paginaHtml(caminhoCompletoConllu, caminhoCompletoHtml, nomePesquisa, dataAgora, conllu, criterio, parametros, numeroOcorrencias, casosOcorrencias, script, fullParameters).montarHtml()

	if nomePesquisa and nomePesquisa not in fastSearch:
		try:
			os.remove("./interrogar-ud/inProgress/{}.inProgress".format(f"{conllu} {criterio} {parametros} {dataAgora.replace(':', '_')}"))
		except:
			pass

	#Printar sem as funções mais importantes caso seja Busca rápida
	if nomePesquisa in fastSearch:
		print(re.sub(r'<button.*?filtrar.*?\n.*?</button>', '', re.sub(r'<button.*?conllu.*?\n.*?</button>', '', re.sub(r'<input.*?checkbox.*?>', '', arquivoHtml))).replace("../../", "../").replace("<br>\n<br>", "").replace('Selecionar múltiplas sentenças', '').replace('Deselecionar todas as sentenças', '').replace('Selecionar todas as sentenças', '').replace('<!--savequery', '').replace('savequery-->', ''))
		exit()
	if script:
		arquivoHtml = arquivoHtml.replace('Exportar resultados para .html', '')

	#if int(criterio) != 5:
	#arquivoHtml = arquivoHtml.replace('Selecionar múltiplas sentenças', '').replace('Deselecionar todas as sentenças', '').replace('Selecionar todas as sentenças', '')

	with open(caminhoCompletoHtml, "w") as f:
		f.write(arquivoHtml)

	queries = ["\t".join([caminhoCompletoHtml, nomePesquisa, numeroOcorrencias, criterio, parametros, conllu, dataAgora])]

	if not os.path.isfile("./interrogar-ud/queries.txt"):
		with open("./interrogar-ud/queries.txt", "w") as f:
			f.write("")
	with open('./interrogar-ud/queries.txt', 'r') as f:
		queries.extend(f.read().splitlines())

	with open('./interrogar-ud/queries.txt', 'w')as f:
		f.write("\n".join(queries))

	print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body onload="redirect()"><script>function redirect() { window.location = "../'+caminhoCompletoHtml+'" }</script></body>')


# get file encoding type
def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']

def definirVariaveisDePesquisa(form):
	if 'scriptQueryFile' in form and form['scriptQueryFile'].value:
		if not os.path.isdir('./cgi-bin/scripts'):
			os.mkdir('./cgi-bin/scripts')
		with open("./interrogar-ud/modelo_query.py") as f:
			modelo_query = f.read()
		with open('./cgi-bin/scripts/' + form['scriptQueryFile'].filename, 'wb') as f:
			f.write(form['scriptQueryFile'].file.read())
		with open("./cgi-bin/scripts/" + form['scriptQueryFile'].filename, encoding=get_encoding_type("./cgi-bin/scripts/" + form['scriptQueryFile'].filename)) as f:
			with open("./cgi-bin/queryScript.py", "w") as w:
				w.write(modelo_query.replace("<!--pesquisa-->", "\n        ".join(f.read().splitlines())))
		script = form['scriptQueryFile'].filename
		parametros = form['scriptQueryFile'].filename
	else:
		script = False

	pesquisa = form['pesquisa'].value.strip()
	if re.search(r'^\d+$', pesquisa.split(' ')[0]):
		criterio = pesquisa.split(' ')[0]
		parametros = pesquisa.split(' ', 1)[1]
	elif any(x in pesquisa for x in [' = ', ' == ', ' != ', ' !== ']) and len(pesquisa.split('"')) > 2:
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
		with open("./cgi-bin/queryScript.py", 'r') as f:
			scriptFile = f.read().replace("<!--corpus-->", caminhoCompletoConllu)
		with open("./cgi-bin/queryScript.py", "w") as f:
			f.write(scriptFile)
		import queryScript
		resultadosBusca = queryScript.getResultadosBusca()

	if not os.path.isdir('./cgi-bin/json'):
		os.mkdir('./cgi-bin/json')
	try:
		with open("./cgi-bin/json/" + slugify(conllu + "_" + parametros + ".json"), "w") as f:
			json.dump(resultadosBusca, f)
	except:
		pass

	numeroOcorrencias = str(len(resultadosBusca['output']))
	casosOcorrencias = resultadosBusca['casos']
	fullParameters = resultadosBusca['parameters']

	return numeroOcorrencias, casosOcorrencias, fullParameters


class paginaHtml():

	def __init__(self, caminhoCompletoConllu, caminhoCompletoHtml, nomePesquisa, dataAgora, conllu, criterio, parametros, numeroOcorrencias, casosOcorrencias, script, fullParameters):
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
		self.fullParameters = fullParameters

	def adicionarHeader(self):
		arquivoHtml = self.arquivoHtml.replace('<title>link de pesquisa 1 (203): Interrogatório</title>', '<title>' + web.escape(self.nomePesquisa) + ' (' + self.numeroOcorrencias + '): Interrogatório</title>')
		casos = f"<span class='translateHtml'>Casos</span>: {str(self.casosOcorrencias)}" if self.casosOcorrencias else ""
		arquivoHtml = arquivoHtml.replace('<h3><span id="combination">link de pesquisa 1</span> (203)</h3>', '<h3><a style="color:black; max-width: 40vw; word-wrap: break-word;" id=titulo><span id=combination>' + web.escape(self.nomePesquisa) + '</span> (' + self.numeroOcorrencias + ')</a></h3>' + casos)

		with open ('./interrogar-ud/criterios.txt', 'r') as f:
			criterios = f.read().split('!@#')
		criterios = [x for x in criterios if x.strip()]

		refazerPesquisa = '<br><span class="translateHtml">Refazer busca</span></a>'
		arquivoHtml = arquivoHtml.replace('<p>critério y#z#k&nbsp;&nbsp;&nbsp; arquivo_UD&nbsp;&nbsp;&nbsp; <span id="data">data</span>&nbsp;&nbsp;&nbsp;', '<p><!--div class=tooltip style="max-width: 60vw; word-wrap: break-word;"--><span class="translateHtml">Busca:</span> <a class="refazerPesquisa translateTitle" title="Refazer busca" href="../../cgi-bin/interrogar.py?corpus=' + self.conllu + '&params=' + self.criterio + ' ' + encodeUrl(self.parametros.replace('"', "'")) + '"><span id=expressao style="word-break: break-all">' + self.criterio + ' ' + web.escape(self.parametros) + '</span></a><!--span class=tooltiptext>' + criterios[int(self.criterio)+1].split('<h4>')[0] + '</span></div-->' + f'<br>Corpus: <span id=corpus>' + self.conllu + '</span><br><br><span id=data><small>' + prettyDate(self.dataAgora.replace('_', ' ')).beautifyDateDMAH() + '</small></span>')
		arquivoHtml = arquivoHtml.replace('id="apagar_link" value="link1"', 'id=apagar_link value="' + slugify(self.nomePesquisa) + '_' + self.dataAgora.replace(':', '_') + '"')

		return arquivoHtml

	def adicionarDistribution(self):
		if self.criterio in ["5", "1"]:
			if self.nomePesquisa not in fastSearch:
				return self.arquivoHtml.replace("!--DIST", "").replace("DIST-->", "><form id=dist target='_blank' action='../../cgi-bin/distribution.py' method=POST><input type=hidden name=notSaved id=html_dist value='{0}'><input type=hidden name=html id=html_dist value='{1}'><input type=hidden name=coluna id=coluna_dist><input id=expressao_dist type=hidden name=expressao><input id=corpus_dist type=hidden name=corpus><input id=combination_dist type=hidden name=combination><input id=link_dist type=hidden name=link_dist></form>".format(self.parametros.replace("'", '"'), self.caminhoCompletoHtml))
			return self.arquivoHtml.replace("!--DIST", "").replace("DIST-->", "><form id=dist target='_blank' action='../cgi-bin/distribution.py' method=POST><input type=hidden name=notSaved id=html_dist value='{0}'><input type=hidden name=coluna id=coluna_dist><input id=expressao_dist type=hidden name=expressao><input id=corpus_dist type=hidden name=corpus><input id=combination_dist type=hidden name=combination><input id=link_dist type=hidden name=link_dist></form>".format(self.parametros.replace("'", '"')))
			#return self.arquivoHtml.replace("DIST-->", 'DIST--><span class="translateHtml"><a href="#" onclick="document.location.href = $(\'.refazerPesquisa\').attr(\'href\') + \'&save=True\';">Salve a busca</a> para visualizar a distribuição das palavras em negrito.</span>')
		return self.arquivoHtml

	def adicionarExecutarScript(self):
		arquivoHtml = self.arquivoHtml.split("<!--script-->")
		arquivoHtml[0] += "<input type=hidden name=criterio value=\"{}\"><input type=hidden name=parametros value=\'{}\'><input type=hidden name=nome_interrogatorio value=\"{}\"><input type=hidden name=occ value=\"{}\"><input type=hidden name=link_interrogatorio value=\"{}\"><input type=hidden name=conllu value=\"{}\"><input type=hidden name=fullParameters value='{}'>".format(
			self.criterio,
			self.parametros,
			web.escape(self.nomePesquisa).replace('"', "&quot;"),
			self.numeroOcorrencias,
			self.caminhoCompletoHtml,
			self.conllu,
			self.fullParameters,
		)	

		return "".join(arquivoHtml)

	def montarHtml(self):
		with open("./interrogar-ud/resultados/link1.html", "r") as f:
			self.arquivoHtml = f.read()
			self.arquivoHtml = self.arquivoHtml.replace("../cgi-bin/modelo_script.py?crit=&params=", f"../cgi-bin/modelo_script.py?crit={self.criterio}&params={encodeUrl(self.fullParameters)}")
			self.arquivoHtml = self.arquivoHtml.replace('../cgi-bin/filtrar.py', '../cgi-bin/filtrar.py?html=' + slugify(self.nomePesquisa) + '_' + self.dataAgora.replace(':', '_') + '&udoriginal=' + self.conllu)
			self.arquivoHtml = self.arquivoHtml.replace('../cgi-bin/conllu.py', '../cgi-bin/conllu.py?html=./interrogar-ud/resultados/' + slugify(self.nomePesquisa) + '_' + self.dataAgora.replace(':', '_') + '.html')

		self.arquivoHtml = self.adicionarHeader()
		if not self.script:
			self.arquivoHtml = self.adicionarDistribution()
			self.arquivoHtml = self.adicionarExecutarScript()
		if self.script:
			self.arquivoHtml = self.arquivoHtml.split("<!--script-->")[0] + f"<input name=queryScript type=hidden value='{slugify(self.script)}'>" + f"<input type=hidden name=conllu value=\"{self.conllu}\">" + f"<input type=hidden name=nome_interrogatorio value=\"{web.escape(self.nomePesquisa)}\">" + f"<input type=hidden name=link_interrogatorio value=\"{self.caminhoCompletoHtml}\">" + self.arquivoHtml.split("<!--script-->")[1]
			self.arquivoHtml = self.arquivoHtml.replace("Correção em lote", "")

		return self.arquivoHtml


if __name__ == "__main__":
	main()
