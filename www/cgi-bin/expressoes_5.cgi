#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import os
import cgi, cgitb
cgitb.enable()
import estrutura_ud
import interrogar_UD
from datetime import datetime
from functions import prettyDate, encodeUrl, fromInterrogarToHtml
import html as web
from functions import corpusGenericoExpressoes

with open("../cgi-bin/expressoes_5.txt") as f:
    fileExpressions = f.read().splitlines()
    expressions = []
    [expressions.append(x) for x in fileExpressions if not x in expressions]

corpus = estrutura_ud.Corpus(recursivo=True)
corpus.load('../cgi-bin/' + corpusGenericoExpressoes)

dictExpressions = [{"expression": x, "example": interrogar_UD.main(corpus, 5, x.split(" ", 1)[1], 1)['output'][0]['resultado']} for x in expressions]

html = "<title class='translateHtml'>Banco de expressões de busca do critério 5: Python</title>\
    <body style='margin:10px auto; max-width:960px;'>\
    <h1 class='translateHtml'>Banco de expressões</h1>\
    <a href='#' class='translateHtml' onclick='window.close()'>Fechar</a><br><br><span class='translateHtml'>Critério 5: Python</span><br>\
        <span class='translateHtml'>Página gerada dia</span> " + prettyDate(datetime.now()).beautifyDateDMAH() \
            + "<hr>\
                <br><table style='margin:auto; border-collapse: collapse;' border='1'><tr><th class='translateHtml'>Expressão</th><th class='translateHtml'>Exemplo</th></tr>"

for expression in dictExpressions:
    sentence = estrutura_ud.Sentence(recursivo=False)
    sentence.build(fromInterrogarToHtml(expression['example']))
    html += f"<tr><td style='padding:10px;'><a target='_blank' style='text-decoration:none; color:blue;' href='../cgi-bin/interrogar.cgi?params={encodeUrl(expression['expression'])}'>" + expression['expression'] + "</a></td><td style='padding:10px;'>" + sentence.text + "</td></tr>"

html += "</table><br><br></body>"
print(html)
