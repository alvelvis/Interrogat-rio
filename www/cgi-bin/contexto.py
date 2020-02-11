#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import cgi, cgitb
cgitb.enable()
import estrutura_ud
import re
from functions import prettyDate
from datetime import datetime

form = cgi.FieldStorage()

corpus = estrutura_ud.Corpus(recursivo=False)
corpus.load('../interrogar-ud/conllu/' + form['corpus'].value)

contextoEsquerda = ["", ""]
contextoDireita = ["", ""]
sent_id = form['sent_id'].value if 'sent_id' in form else ""
id = form['id'].value if 'id' in form else ""
conllu = form['corpus'].value

numero = re.search(r'^\d+$', sent_id.rsplit('-', 1)[1])[0] if '-' in sent_id else id
identificador = sent_id.rsplit("-", 1)[0] + "-" if '-' in sent_id else ""

contextoEsquerda = []
contextoDireita = []

for i in range(int(numero)-1):
    if identificador + str(i + 1) in corpus.sentences:
        contextoEsquerda.append([identificador + str(i+1), corpus.sentences[identificador + str(i+1)].text])

i = int(numero)
while True:
    if identificador + str(i+1) in corpus.sentences:
        contextoDireita.append([identificador + str(i+1), corpus.sentences[identificador + str(i+1)].text])
        i += 1
    else:
        break

html = [f'<title>Contexto - Interrogatório</title><h1>Contexto</h1><a href="javascript:window.close()">Fechar</a><hr>Página gerada dia {prettyDate(datetime.now()).beautifyDateDMAH()}<br>Corpus: <a href="../interrogar-ud/conllu/{conllu}" download>{conllu}</a><h4><a href="#negrito">Pular para {sent_id or id}</a></h4>']
[html.append("<hr>{}: {}".format(x[0], x[1])) for x in contextoEsquerda]
html += [f"<hr><b> <div id='negrito'>{sent_id or id}: {corpus.sentences[sent_id].text or corpus.sentences[id].text}</div></b>"]
[html.append("<hr>{}: {}".format(x[0], x[1])) for x in contextoDireita]
print("".join(html))