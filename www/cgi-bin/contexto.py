#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import cgi, cgitb
cgitb.enable()
import estrutura_ud
import re
import html as web
from utils import prettyDate
from datetime import datetime

form = cgi.FieldStorage()

sent_id = form['sent_id'].value if 'sent_id' in form else ""
id = form['id'].value if 'id' in form else ""
conllu = form['corpus'].value

numero = re.search(r'^\d+$', sent_id.rsplit('-', 1)[1])[0] if '-' in sent_id else sent_id
identificador = sent_id.rsplit("-", 1)[0] + "-" if '-' in sent_id else ""

corpus = estrutura_ud.Corpus(recursivo=False, keywords=[re.escape(identificador)])
corpus.load('./interrogar-ud/conllu/' + form['corpus'].value)

contextoEsquerda = []
contextoDireita = []

for i in range(int(numero)-1):
    if identificador + str(i + 1) in corpus.sentences:
        contextoEsquerda.append([identificador + str(i+1), corpus.sentences[identificador + str(i+1)].text])

all_sentences = [x for x in corpus.sentences if not identificador or x.rsplit("-", 1)[0] + "-" == identificador]
for sentence in all_sentences:
    if (int(sentence.rsplit("-", 1)[1]) if identificador else int(sentence)) > int(numero):
        contextoDireita.append([sentence, corpus.sentences[sentence].text])

html = [f'<script src="../interrogar-ud/jquery.min.js"></script><script src="../interrogar-ud/resultados.js?version=12"></script><title class="translateHtml">Contexto: Interrogatório</title><h1 class="translateHtml">Contexto</h1><!--a href="javascript:window.close()" class="translateHtml">Fechar</a--><hr><span class="translateHtml">Página gerada dia</span> {prettyDate(datetime.now()).beautifyDateDMAH()}<br><span class="translateHtml">Corpus:</span> <a href="../interrogar-ud/conllu/{conllu}" download>{conllu}</a><h4><a href="#negrito" style="color:blue"><span class="translateHtml">Pular para</span> {sent_id or id}</a></h4>']
[html.append("<hr>{}: {}".format(x[0], web.escape(x[1]))) for x in contextoEsquerda]
html += [f"<hr><b> <div id='negrito'>{sent_id or id}: {web.escape(corpus.sentences[sent_id].text) or web.escape(corpus.sentences[id].text)}</div></b>"]
[html.append("<hr>{}: {}".format(x[0], web.escape(x[1]))) for x in contextoDireita]
print("".join(html))