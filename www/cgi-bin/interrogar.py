#!../.interrogatorio/bin/python3
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
from utils import tabela, prettyDate, encodeUrl, save_query_json, fastsearch
import html as web
import time
import sys
import json

def main():
	if not os.path.isdir("./interrogar-ud/conllu"):
		os.mkdir("./interrogar-ud/conllu")

	sendRequestInterrogar() if os.environ['REQUEST_METHOD'] != "POST" else sendPOSTInterrogar()

def sendRequestInterrogar():

	# delete old queries
	json_path = "./cgi-bin/json"
	json_query_path = os.path.join(json_path, "query_records.json")
	if os.path.isfile(json_query_path):
		with open(json_query_path) as f:
			query_records = json.loads(f.read())
		for filename in os.listdir(json_path):
			if filename in ["query_records.json", "filtros.json"]:
				continue
			filename_json_id = filename.split(".json")[0]
			if not filename_json_id in query_records:
				os.remove(os.path.join(json_path, filename))
			else:
				date = datetime.fromisoformat(query_records[filename_json_id]['datetime'])
				time_passed = datetime.now() - date
				if time_passed.days >= 2 and query_records[filename_json_id]['persistent'] == False:
					os.remove(os.path.join(json_path, filename))
	
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
		criteriosBusca = [("[<a href='#' class='toggleCriteria translateHtml' onclick=\"$('.queryString').hide(); $('.normalQuery').show();\" criterio='-1'>Voltar</a>]<br>" if i != 0 else "") + x for i, x in enumerate(criteriosBusca) if x.strip()]

	paginaHTML[0] += "\n".join(["<div class='container-lr criterio' {2} id=criterio_{0}>{1}</div>".format(i-1, criterio, " style='display:none'" if i-1 != -1 else "") for i, criterio in enumerate(criteriosBusca)])

	paginaHTML = "".join(paginaHTML)
	paginaHTML = paginaHTML.split("<!--corpora-cloud-->")[0] + " ".join(corpora_cloud) + paginaHTML.split("<!--corpora-cloud-->")[1]
	paginaHTML = paginaHTML.split("<!--selectpicker-->")[0] + "<option style='display:none' class='translateHtml' disabled selected value> -- escolha um corpus -- </option>" + "\n".join(arquivosCONLLU) + paginaHTML.split("<!--selectpicker-->")[1]

	refazerPesquisa = cgi.FieldStorage()['params'].value if 'params' in cgi.FieldStorage() else "" #.replace("'", '"')
	refazerCorpus = cgi.FieldStorage()['corpus'].value if 'corpus' in cgi.FieldStorage() else ""
	refazerNome = cgi.FieldStorage()['nome'].value if 'nome' in cgi.FieldStorage() else "Busca salva"
	paginaHTML = paginaHTML.replace('id="pesquisa"', f'''id="pesquisa" value='{web.escape(refazerPesquisa)}\'''')\
						.replace(f"value='{refazerCorpus}'", f"value='{refazerCorpus}' selected")\
						.replace('name="nome" value="Busca salva"', f'name="nome" value=\'{web.escape(refazerNome)}\'')
	if 'save' in cgi.FieldStorage():
		paginaHTML = paginaHTML.replace('checked><div onclick="$(\'.toggleRapida\')', '><div onclick="$(\'.toggleRapida\')').replace('><div onclick="$(\'.toggleSalvar\')', 'checked><div onclick="$(\'.toggleSalvar\')"')
	if 'go' in cgi.FieldStorage():
		paginaHTML = paginaHTML.split("</body>")[0] + '<script>$("body").ready(function(){$("#enviar").click()})</script>' + "</body>" + paginaHTML.split("</body>")[1]
	print(paginaHTML)


def sendPOSTInterrogar():
	criterio, parametros, conllu, nomePesquisa, script = definirVariaveisDePesquisa(cgi.FieldStorage())

	caminhoCompletoConllu = "./interrogar-ud/conllu/" + conllu
	dataAgora = str(datetime.now()).replace(' ', '_')

	if nomePesquisa and nomePesquisa not in fastsearch:
		try:
			with open("./interrogar-ud/inProgress/{}.inProgress".format(f"{conllu} {criterio} {parametros} {dataAgora.replace(':', '_')}"), 'w') as f:
				f.write("")
		except:
			pass
		fast = False
	else:
		fast = True

	numeroOcorrencias, casosOcorrencias, fullParameters, json_id, scriptParams = realizarBusca(conllu, caminhoCompletoConllu, int(criterio), parametros, script, fast, name=nomePesquisa)
	
	caminhoCompletoHtml = './interrogar-ud/resultados/' + slugify(nomePesquisa) + '-' + json_id + '.html'

	arquivoHtml = paginaHtml(caminhoCompletoConllu, caminhoCompletoHtml, nomePesquisa, dataAgora, conllu, criterio, parametros if not script else scriptParams, numeroOcorrencias, casosOcorrencias, script, fullParameters, json_id).montarHtml()

	if nomePesquisa and nomePesquisa not in fastsearch:
		try:
			os.remove("./interrogar-ud/inProgress/{}.inProgress".format(f"{conllu} {criterio} {parametros} {dataAgora.replace(':', '_')}"))
		except:
			pass

	#Printar sem as funções mais importantes caso seja Busca rápida
	if nomePesquisa in fastsearch:
		print(re.sub(r'<button.*?filtrar.*?</button>', '', re.sub(r'<button.*?conllu.*?\n.*?</button>', '', re.sub(r'<input.*?checkbox.*?>', '', arquivoHtml))).replace("../../", "../").replace("<br>\n<br>", "").replace('<!--savequery', '').replace('savequery-->', ''))
		exit()
	if script:
		arquivoHtml = arquivoHtml.replace('Exportar resultados para .html', '')

	with open(caminhoCompletoHtml, "w") as f:
		f.write(arquivoHtml)

	queries = ["\t".join([caminhoCompletoHtml, nomePesquisa, numeroOcorrencias, criterio, parametros, conllu, dataAgora, json_id])]

	if not os.path.isfile("./interrogar-ud/queries.txt"):
		with open("./interrogar-ud/queries.txt", "w") as f:
			f.write("")
	with open('./interrogar-ud/queries.txt', 'r') as f:
		queries.extend(f.read().splitlines())

	with open('./interrogar-ud/queries.txt', 'w')as f:
		f.write("\n".join(queries))

	print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body onload="redirect()"><script>function redirect() { window.location = "../'+caminhoCompletoHtml+'" }</script></body>')

def definirVariaveisDePesquisa(form):
	if 'scriptQueryFile' in form and form['scriptQueryFile'].value:
		if not os.path.isdir('./cgi-bin/scripts'):
			os.mkdir('./cgi-bin/scripts')
		with open("./interrogar-ud/modelo-query.txt") as f:
			modelo_query = f.read()
		with open('./cgi-bin/scripts/' + form['scriptQueryFile'].filename, 'wb') as f:
			f.write(form['scriptQueryFile'].file.read())
		with open("./cgi-bin/scripts/" + form['scriptQueryFile'].filename) as f:
			with open("./cgi-bin/queryScript.py", "w") as w:
				w.write(modelo_query.replace("<!--pesquisa-->", "\n        ".join(f.read().replace("\t", "    ").splitlines())))
		script = form['scriptQueryFile'].filename
	else:
		script = False

	pesquisa = form['pesquisa'].value.strip()
	if re.search(r'^\d+$', pesquisa.split(' ')[0]) and ' ' in pesquisa:
		criterio = pesquisa.split(' ')[0]
		parametros = pesquisa.split(' ', 1)[1]
	elif len(pesquisa.split('"')) > 2 or any(x in pesquisa for x in ["==", " = ", " != "]) or "tokens=" in pesquisa or script:
		criterio = '5'
		parametros = pesquisa
	else:
		criterio = '1'
		parametros = pesquisa

	conllu = form['conllu'].value
	nomePesquisa = 'Busca rápida' if form['meth'].value != 'salvar' else form['nome'].value
	#sentLimit = int(form['sentLimit'].value) if 'sentLimit' in form and form['meth'].value == 'salvar' else 0

	return criterio, parametros, conllu, nomePesquisa, script


def realizarBusca(conllu, caminhoCompletoConllu, criterio, parametros, script="", fast=False, name=""):
	if not script:
		resultadosBusca = interrogar_UD.main(caminhoCompletoConllu, criterio, parametros, fastSearch=True)
	else:
		with open("./cgi-bin/queryScript.py", 'r') as f:
			scriptFile = f.read().replace("<!--corpus-->", caminhoCompletoConllu)
		with open("./cgi-bin/queryScript.py", "w") as f:
			f.write(scriptFile)
		try:
			import queryScript
		except IndentationError:
			print("Erro: verifique a indentação do arquivo de script.")
			exit()
		resultadosBusca = queryScript.getResultadosBusca()
	
	json_id = save_query_json(resultadosBusca, persistent=not fast, name=name)

	numeroOcorrencias = str(len(resultadosBusca['output']))
	casosOcorrencias = resultadosBusca['casos']
	fullParameters = resultadosBusca['parameters']
	scriptParams = resultadosBusca['scriptParams'] if script else ""

	return numeroOcorrencias, casosOcorrencias, fullParameters, json_id, scriptParams


class paginaHtml():

	def __init__(self, caminhoCompletoConllu, caminhoCompletoHtml, nomePesquisa, dataAgora, conllu, criterio, parametros, numeroOcorrencias, casosOcorrencias, script, fullParameters, json_id):
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
		self.json_id = json_id

	def adicionarHeader(self):
		arquivoHtml = self.arquivoHtml.replace('<title>link de pesquisa 1 (203): Interrogatório</title>', '<title>' + web.escape(self.nomePesquisa) + ' (' + self.numeroOcorrencias + '): Interrogatório</title>')
		casos = f"<span style=\"font-weight:bold\"><span class='translateHtml'>Casos</span></span>: {str(self.casosOcorrencias)}" if self.casosOcorrencias else ""
		arquivoHtml = arquivoHtml.replace('<h3><span id="combination">link de pesquisa 1</span> (203)</h3>', '<h3><a style="color:black; max-width: 40vw; word-wrap: break-word;" id=titulo><span id=combination>' + web.escape(self.nomePesquisa) + '</span> (' + self.numeroOcorrencias + ')</a></h3>' + casos)

		with open ('./interrogar-ud/criterios.txt', 'r') as f:
			criterios = f.read().split('!@#')
		criterios = [x for x in criterios if x.strip()]

		refazerPesquisa = '<br><span class="translateHtml">Refazer busca</span></a>'
		arquivoHtml = arquivoHtml.replace('<p>critério y#z#k&nbsp;&nbsp;&nbsp; arquivo_UD&nbsp;&nbsp;&nbsp; <span id="data">data</span>&nbsp;&nbsp;&nbsp;', '<div><div style="margin-top:2px; margin-bottom:2px;"><span class="translateHtml" style="font-weight:bold">Busca:</span> <span id=expressao style="word-break: break-all">' + web.escape(self.parametros) + '</span>' + f'</div><span style="font-weight:bold">Corpus:</span> <span id=corpus>' + self.conllu + '</span><br><br>[<a href="#" class="newQueryFromResults translateHtml">Tentar outra busca</a>]' + (' [<a href="#" id="salvarBusca" class="translateHtml">Salvar busca</a>]' if self.nomePesquisa in fastsearch else "") + ' [<a class="refazerPesquisa translateHtml" href="../../cgi-bin/interrogar.py?corpus=' + encodeUrl(self.conllu) + '&params=' + encodeUrl(self.parametros) + '">Voltar</a>]<br><br><span id=data><small>' + prettyDate(self.dataAgora.replace('_', ' ')).beautifyDateDMAH() + '</small></span></div>')
		arquivoHtml = arquivoHtml.replace('id="apagar_link" value="link1"', 'id=apagar_link value="' + slugify(self.nomePesquisa) + '-' + self.json_id + '"')
		arquivoHtml = arquivoHtml.replace('<input type="hidden" id="jsonId" value="0">', '<input type="hidden" id="jsonId" name="jsonId" value="%s">' % self.json_id)

		return arquivoHtml

	def adicionarDistribution(self):
		if self.criterio in ["5", "1"]:			
			if self.nomePesquisa not in fastsearch:
				return self.arquivoHtml.replace("!--DIST", "").replace("DIST-->", "><form id=dist target='_blank' action='../../cgi-bin/distribution.py' method=POST><input type=hidden name=notSaved id=html_dist value='{0}'><input type=hidden name=html id=html_dist value='{1}'><input type=hidden name=coluna id=coluna_dist><input id=expressao_dist type=hidden name=expressao><input id=corpus_dist type=hidden name=corpus><input id=combination_dist type=hidden name=combination><input id=link_dist type=hidden name=link_dist></form>".format(self.parametros.replace("'", '"'), self.caminhoCompletoHtml)).replace("<input type=hidden name=coluna id=coluna_dist>", '<input type=hidden name=coluna id=coluna_dist><input type="hidden" id="jsonId" name="jsonId" value="%s">' % self.json_id)
			return self.arquivoHtml.replace("!--DIST", "").replace("DIST-->", "><form id=dist target='_blank' action='../cgi-bin/distribution.py' method=POST><input type=hidden name=notSaved id=html_dist value='{0}'><input type=hidden name=coluna id=coluna_dist><input id=expressao_dist type=hidden name=expressao><input id=corpus_dist type=hidden name=corpus><input id=combination_dist type=hidden name=combination><input id=link_dist type=hidden name=link_dist></form>".format(self.parametros.replace("'", '"'))).replace("<input type=hidden name=coluna id=coluna_dist>", '<input type=hidden name=coluna id=coluna_dist><input type="hidden" id="jsonId" name="jsonId" value="%s">' % self.json_id)
			#return self.arquivoHtml.replace("DIST-->", 'DIST--><span class="translateHtml">Salve a busca para visualizar a distribuição das palavras em negrito.</span>')
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
			self.arquivoHtml = self.arquivoHtml.replace("../cgi-bin/download_batch_correction.py?crit=&params=", f"../cgi-bin/download_batch_correction.py?crit={self.criterio}&params={encodeUrl(self.fullParameters)}")
			self.arquivoHtml = self.arquivoHtml.replace('../cgi-bin/filtrar.py', '../cgi-bin/filtrar.py?html=' + slugify(self.nomePesquisa) + '_' + self.json_id + '&udoriginal=' + self.conllu)
			self.arquivoHtml = self.arquivoHtml.replace('../cgi-bin/conllu.py', '../cgi-bin/conllu.py?html=./interrogar-ud/resultados/' + slugify(self.nomePesquisa) + '_' + self.json_id + '.html')

		self.arquivoHtml = self.adicionarHeader()
		#if not self.script:
		self.arquivoHtml = self.adicionarDistribution()
		self.arquivoHtml = self.adicionarExecutarScript()
		#if self.script:
			#self.arquivoHtml = self.arquivoHtml.split("<!--script-->")[0] + f"<input name=queryScript type=hidden value='{slugify(self.script)}'>" + f"<input type=hidden name=conllu value=\"{self.conllu}\">" + f"<input type=hidden name=nome_interrogatorio value=\"{web.escape(self.nomePesquisa)}\">" + f"<input type=hidden name=link_interrogatorio value=\"{self.caminhoCompletoHtml}\">" + self.arquivoHtml.split("<!--script-->")[1]
			#self.arquivoHtml = self.arquivoHtml.replace("Correção em lote", "")

		return self.arquivoHtml


if __name__ == "__main__":
	main()
