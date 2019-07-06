#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html")
print('\n\n')

import os
import cgi,cgitb
cgitb.enable()
import re
from datetime import datetime
from functions import tabela
import html as web
import estrutura_ud

#if not 'REQUEST_METHOD' in os.environ:
#	os.environ['REQUEST_METHOD'] = 'POST'

from estrutura_dados import slugify as slugify

#POST
form = cgi.FieldStorage()
with open(form['html'].value, 'r') as f:
	html = f.read()
	html = web.unescape(html)
	html = re.split(r'\<pre id=.*?\>', html)#html = re.split(r'\<pre.*?\>', html)
	html = [x.split('</pre>')[0] for x in html[1:]]
	corpus = list()
	
	for sentence in html:
		sent = estrutura_ud.Sentence()
		sent.build(sentence.replace('<font color="' + tabela['yellow'] + '">','').replace('<font color="' + tabela['red'] + '">','').replace('<font color="' + tabela['cyan'] + '">','').replace('<font color="' + tabela['blue'] + '">','').replace('<font color="' + tabela['purple'] + '">','').replace('</font>',''))
		corpus.append(sent)

	dist = list()
	for sentence in corpus:
		for token in sentence.tokens:
			if '<b>' in token.to_str() or "</b>" in token.to_str():
				if form["coluna"].value == "id": dist.append(token.id)
				if form["coluna"].value == "word": dist.append(token.word)
				if form["coluna"].value == "lemma": dist.append(token.lemma)
				if form["coluna"].value == "upos": dist.append(token.upos)
				if form["coluna"].value == "xpos": dist.append(token.xpos)
				if form["coluna"].value == "feats": dist.append(token.feats)
				if form["coluna"].value == "dephead": dist.append(token.dephead)
				if form["coluna"].value == "deprel": dist.append(token.deprel)
				if form["coluna"].value == "deps": dist.append(token.deps)
				if form["coluna"].value == "misc": dist.append(token.misc)

	dicionario = dict()
	for entrada in dist:
		entrada = entrada.replace("<b>", "").replace("</b>", "")
		if not entrada in dicionario: dicionario[entrada] = 1
		else: dicionario[entrada] += 1
	
	lista = list()
	for entrada in dicionario:
		lista.append((entrada, dicionario[entrada]))

	pagina = "<h1>Distribuição de '" + form["coluna"].value + "' em " + form["combination"].value + "</h1><hr>Corpus: <a href='../interrogar-ud/conllu/"+form["corpus"].value+"'>" + form["corpus"].value + "</a><br>" + form["expressao"].value + "<br><br>Quantidade de entradas: "+str(len(dist))+"<br>Quantidade de "+form["coluna"].value+" diferentes: "+str(len(lista))+"<br><br>"

	freq = dict()
	for entrada in dicionario:
		if not dicionario[entrada] in freq: freq[dicionario[entrada]] = 1
		else: freq[dicionario[entrada]] += 1
	lista_freq = list()
	for entrada in freq:
		lista_freq.append((entrada, freq[entrada]))

	pagina += "<table><tr><th>"+form["coluna"].value+"</th><th>Frequência</th></tr>"
	for entrada in sorted(lista, key=lambda x: x[1], reverse=True):
		pagina += "<tr><td>" + cgi.escape(entrada[0]) + "</td><td>" + str(entrada[1]) + "</td></tr>"
	pagina += "</table>"

	pagina += "<br><br><table><tr><th>Frequência</th><th>Quantidade de "+form["coluna"].value+" diferentes</th></tr>"
	for entrada in sorted(lista_freq, key=lambda x: x[0], reverse=True):
		pagina += "<tr><td>" + str(entrada[0]) + "</td><td>" + str(entrada[1]) + "</td></tr>"
	pagina += "</table>"

print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body>' + pagina + '</body>') #window.location="' + form['html'].value


