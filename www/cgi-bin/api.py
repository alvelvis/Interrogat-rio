#!/usr/bin/python3
# -*- coding: UTF-8 -*-

fastSearch = ['teste', 'Busca rápida']

print("Content-type:application/json; charset=utf-8")
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
import json

def renderSentences(script=""):

    form = cgi.FieldStorage()

    conllu = form['conllu'].value
    corpus = conllu
    caminhoCompletoConllu = '../interrogar-ud/conllu/' + conllu
    caminhoCompletoHtml = form['html'].value

    parametros = form['parametros'].value.split(" ", 1)[1]
    criterio = int(form['parametros'].value.split(" ", 1)[0])

    if "script" in form:
        script = form['script'].value

    startPoint = int(form['indexSentences'].value)
    nomePesquisa = form['nomePesquisa'].value

    if not script:
        resultadosBusca = interrogar_UD.main(caminhoCompletoConllu, criterio, parametros)
    else:
        if os.system("cp ../cgi-bin/scripts/" + script + ' ../cgi-bin/queryScript.py'):
            pass
        with open("../cgi-bin/queryScript.py", 'r') as f:
            scriptFile = f.read().replace("<!--corpus-->", caminhoCompletoConllu)
        with open("../cgi-bin/queryScript.py", "w") as f:
            f.write(scriptFile)
        import queryScript
        resultadosBusca = queryScript.getResultadosBusca()


    numeroOcorrencias = len(resultadosBusca['output'])
    if numeroOcorrencias > startPoint + 51 and numeroOcorrencias >= 1:
        finalPoint = startPoint + 50
        noMore = False
    else:
        finalPoint = len(resultadosBusca['output'])
        noMore = True

    arquivoHtml = ""
    for i, ocorrencia in enumerate(resultadosBusca['output'][startPoint:finalPoint]):
        arquivoHtml += '<div class=container>\n'
        arquivoHtml += f'<p>{str(startPoint+i+1)}/{numeroOcorrencias}</p>' + '\n'
        if ocorrencia['resultadoEstruturado'].sent_id:
            arquivoHtml += f'''<p><!--input class=cb id=checkbox_{str(startPoint+i+1)} style="margin-left:0px;" title="Selecionar sentença para filtragem" type=checkbox-->{ocorrencia['resultadoEstruturado'].sent_id}</p>''' + '\n'
        arquivoHtml += f"<p><span id=text_{str(startPoint+i+1)}>{ocorrencia['resultadoAnotado'].text.replace('/BOLD', '</b>').replace('@BOLD', '<b>').replace('@YELLOW/', '<font color=' + tabela['yellow'] + '>').replace('@PURPLE/', '<font color=' + tabela['purple'] + '>').replace('@BLUE/', '<font color=' + tabela['blue'] + '>').replace('@RED/', '<font color=' + tabela['red'] + '>').replace('@CYAN/', '<font color=' + tabela['cyan'] + '>').replace('/FONT', '</font>')}</span></p>" + '\n'
        if ((ocorrencia['resultadoEstruturado'].sent_id and ('-' in ocorrencia['resultadoEstruturado'].sent_id or re.search(r'^\d+$', ocorrencia['resultadoEstruturado'].sent_id))) or ocorrencia['resultadoEstruturado'].id) and ocorrencia['resultadoEstruturado'].text:
            arquivoHtml += f"<p><input id=contexto_{str(startPoint+i+1)} value=\"Mostrar contexto\" onclick=\"contexto('{ocorrencia['resultadoEstruturado'].sent_id}', '{ocorrencia['resultadoEstruturado'].id}', '{corpus}')\" style=\"margin-left:0px\" type=button> <input id=mostrar_{str(startPoint+i+1)} class=anotacao value=\"Mostrar anotação\" onclick=\"mostrar('div_{str(startPoint+i+1)}', 'mostrar_{str(startPoint+i+1)}')\" style=\"margin-left:0px\" type=button> <input id=opt_{str(startPoint+i+1)} class=opt value=\"Mostrar opções\" onclick=\"mostraropt('optdiv_{str(startPoint+i+1)}', 'opt_{str(startPoint+i+1)}')\" style=\"margin-left:0px\" type=button> <input class=\"abrirInquerito\" type=button value=\"Abrir inquérito\" onclick='inquerito(\"form_{str(startPoint+i+1)}\")'></p>" + "\n"
        else:
            arquivoHtml += f"<p><input id=mostrar_{str(startPoint+i+1)} class=anotacao value=\"Mostrar anotação\" onclick=\"mostrar('div_{str(startPoint+i+1)}', 'mostrar_{str(startPoint+i+1)}')\" style=\"margin-left:0px\" type=button> <input id=opt_{str(startPoint+i+1)} class=opt value=\"Mostrar opções\" onclick=\"mostraropt('optdiv_{str(startPoint+i+1)}', 'opt_{str(startPoint+i+1)}')\" style=\"margin-left:0px\" type=button> <input type=button value=\"Abrir inquérito\" onclick='inquerito(\"form_{str(startPoint+i+1)}\")'></p>" + '\n'
        arquivoHtml += f"<span style=\"display:none; padding-left:20px;\" id=\"optdiv_{str(startPoint+i+1)}\">"
        arquivoHtml += f"<form action=\"../../cgi-bin/inquerito.py?conllu={conllu}\" target=\"_blank\" method=POST id=form_{str(startPoint+i+1)}><input type=hidden name=sentid value=\"{ocorrencia['resultadoEstruturado'].sent_id}\"><input type=hidden name=occ value=\"{numeroOcorrencias}\"><input type=hidden name=textheader value=\"{ocorrencia['resultadoEstruturado'].text}\"><input type=hidden name=nome_interrogatorio value=\"{cgi.escape(nomePesquisa)}\"><input type=hidden name=link_interrogatorio value=\"{caminhoCompletoHtml}\">"
        if "@BOLD" in ocorrencia['resultadoAnotado'].to_str():
            arquivoHtml += f"<input type=hidden name=tokenId value=\"" + "".join([functions.cleanEstruturaUD(x.id) for x in ocorrencia['resultadoAnotado'].tokens if '@BOLD' in x.to_str()]) + "\">"
        arquivoHtml += "</form>"
        if nomePesquisa not in fastSearch: arquivoHtml += f"<!--a style=\"cursor:pointer\" onclick='filtraragora(\"{str(startPoint+i+1)}\")'>Separar sentença</a-->"
        #arquivoHtml += '<br>'
        arquivoHtml += f"<form action=\"../../cgi-bin/udpipe.py?conllu={conllu}\" target=\"_blank\" method=POST id=udpipe_{str(startPoint+i+1)}><input type=hidden name=textheader value=\"{ocorrencia['resultadoEstruturado'].text}\"></form><a style=\"cursor:pointer\" onclick='anotarudpipe(\"udpipe_{str(startPoint+i+1)}\")'>Anotar frase com o UDPipe</a>"
        arquivoHtml += '<br>'
        arquivoHtml += f"<form action=\"../../cgi-bin/draw_tree.py?conllu={conllu}\" target=\"_blank\" method=POST id=tree_{str(startPoint+i+1)}><input type=hidden name=sent_id value=\"{ocorrencia['resultadoEstruturado'].sent_id}\"><input type=hidden name=text value=\"{ocorrencia['resultadoEstruturado'].text}\"></form><a style=\"cursor:pointer\" onclick='drawtree(\"tree_{str(startPoint+i+1)}\")'>Visualizar árvore de dependências</a>"
        arquivoHtml += '</p></span>\n'
        arquivoHtml += f"<pre id=div_{str(startPoint+i+1)} style=\"display:none\">{ocorrencia['resultadoAnotado'].to_str().replace('/BOLD', '</b>').replace('@BOLD', '<b>').replace('@YELLOW/', '<font color=' + tabela['yellow'] + '>').replace('@PURPLE/', '<font color=' + tabela['purple'] + '>').replace('@BLUE/', '<font color=' + tabela['blue'] + '>').replace('@RED/', '<font color=' + tabela['red'] + '>').replace('@CYAN/', '<font color=' + tabela['cyan'] + '>').replace('/FONT', '</font>')}</pre>" + '\n'
        arquivoHtml += '</div>\n'

 #   sys.stderr.write(arquivoHtml + str(noMore) + str(finalPoint))
  #  sys.stderr.flush()

    print(json.JSONEncoder().encode({
            'success': True,
            'html': arquivoHtml,
            'noMore': noMore,
            'indexSentences': finalPoint,
        }))

if os.environ['REQUEST_METHOD'] == "POST":
    start = time.time()
    renderSentences()
    sys.stderr.write('\nrenderSentences: ' + str(time.time() - start))
