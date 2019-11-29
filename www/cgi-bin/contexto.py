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

if sent_id:
    if '-' in sent_id and re.search(r'^\d+$', sent_id.rsplit('-', 1)[1]):
        contextoEsquerda = [sent_id.rsplit('-', 1)[0] + '-' + str(int(sent_id.rsplit('-', 1)[1]) - 1), corpus.sentences[sent_id.rsplit('-', 1)[0] + '-' + str(int(sent_id.rsplit('-', 1)[1]) - 1)].text] if sent_id.rsplit('-', 1)[0] + '-' + str(int(sent_id.rsplit('-', 1)[1]) - 1) in corpus.sentences else ["", ""]
        contextoDireita = [sent_id.rsplit('-', 1)[0] + '-' + str(int(sent_id.rsplit('-', 1)[1]) + 1), corpus.sentences[sent_id.rsplit('-', 1)[0] + '-' + str(int(sent_id.rsplit('-', 1)[1]) + 1)].text] if sent_id.rsplit('-', 1)[0] + '-' + str(int(sent_id.rsplit('-', 1)[1]) + 1) in corpus.sentences else ["", ""]

    elif re.search(r'^\d+$', sent_id):
        contextoEsquerda = [str(int(sent_id) - 1), corpus.sentences[str(int(sent_id) - 1)].text] if str(int(sent_id) - 1) in corpus.sentences else ["", ""]
        contextoDireita = [str(int(sent_id) - 1), corpus.sentences[str(int(sent_id) + 1)].text] if str(int(sent_id) + 1) in corpus.sentences else ["", ""]

elif id:
    if re.search(r'^\d+$', id):
        contextoEsquerda = corpus.sentences[str(int(id) - 1)].text if str(int(id) - 1) in corpus.sentences else ""
        contextoDireita = corpus.sentences[str(int(id) + 1)].text if str(int(id) + 1) in corpus.sentences else ""

print(f'<title>Contexto - Interrogatório</title><h1>Contexto</h1><a href="javascript:window.close()">Fechar</a><hr>Página gerada dia {prettyDate(datetime.now()).beautifyDateDMAH()}<br>Corpus: <a href="../interrogar-ud/conllu/{conllu}" download>{conllu}</a><br>Sent_id: {sent_id}<br><br>{contextoEsquerda[0]}: {contextoEsquerda[1]}<br><b>{sent_id}</b>: {corpus.sentences[sent_id].text}<br>{contextoDireita[0]}: {contextoDireita[1]}')