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

form = cgi.FieldStorage()

def loadCorpus(ud, size="0.0", updateCorpus=False):
    
    conllus = {}
    if os.path.isfile("../interrogar-ud/conllu.json"):
        with open("../interrogar-ud/conllu.json") as f:
            conllus = json.load(f)

    n_sent = 0
    n_tokens = 0
    n_files = 0
    files = []

    if (updateCorpus) or (size and float(size) < 50.0) or (ud in conllus):
        try:
            if not ud in conllus or updateCorpus:
                conllus[ud] = {}
                with open("../interrogar-ud/conllu/" + ud) as f:
                    for line in f:
                        if line.strip().startswith('# sent_id = '):
                            n_sent += 1
                            if '-' in line:
                                filename = line.rsplit("# sent_id = ", 1)[1].rsplit("-", 1)[0].strip()
                                if not filename in files:
                                    files.append(filename)
                        if line and not line.strip().startswith('#') and len(line.split("\t")) > 5 and not '-' in line.split("\t")[0]:
                            n_tokens += 1
                n_files = len(files)
                conllus[ud]['n_sent'] = n_sent
                conllus[ud]['n_tokens'] = n_tokens
                conllus[ud]['n_files'] = n_files
                with open("../interrogar-ud/conllu.json", "w") as f:
                    json.dump(conllus, f)
            else:
                n_sent = conllus[ud]['n_sent']
                n_tokens = conllus[ud]['n_tokens']
                n_files = conllus[ud]['n_files'] if 'n_files' in conllus[ud] else "NEEDS UPDATE"
            print(json.JSONEncoder().encode({'success': True, 'n_sent': n_sent, 'n_tokens': n_tokens, 'n_files': n_files if n_files else 1, 'ud': ud}))
        except Exception as e:
            sys.stderr.write(str(e))
            print(json.JSONEncoder().encode({'success': True, 'n_sent': "MEMORY_LEAK", 'n_tokens': "MEMORY_LEAK", 'n_files': 'MEMORY_LEAK', 'ud': ud}))
    else:
        print(json.JSONEncoder().encode({'success': True, 'n_sent': "NEEDS UPDATE", 'n_tokens': "NEEDS UPDATE", 'n_files': 'NEEDS UPDATE', 'ud': ud}))

def renderSentences(script=""):

    conllu = form['conllu'].value
    corpus = conllu
    caminhoCompletoConllu = '../interrogar-ud/conllu/' + conllu
    caminhoCompletoHtml = form['html'].value

    parametros = form['parametros'].value.split(" ", 1)[1]
    criterio = int(form['parametros'].value.split(" ", 1)[0])

    if "script" in form:
        script = form['script'].value

    startPoint = int(form['indexSentences'].value)
    filtradoPrevious = int(form['filtrado'].value) if 'filtrado' in form else 0
    nomePesquisa = form['nomePesquisa'].value

    filtros = []
    filtrar_filtros = ""
    pagina_filtros = ""
    if nomePesquisa not in fastSearch:
        pagina_html = caminhoCompletoHtml.rsplit("/", 1)[1].rsplit(".", 1)[0]
        if os.path.isfile("../cgi-bin/filtros.json"):
            with open("../cgi-bin/filtros.json") as f:
                filtros_json = json.load(f)
            filtrar_filtros = "<h4 class='translateHtml'>Filtros já aplicados:</h4>" if pagina_html in filtros_json and filtros_json[pagina_html]['filtros'] else ""
            if pagina_html in filtros_json:
                filtros = [x for nome in filtros_json[pagina_html]['filtros'] for x in filtros_json[pagina_html]['filtros'][nome]['sentences']]
                for pagina in [[x, len(filtros_json[pagina_html]['filtros'][x]['sentences'])] for x in filtros_json[pagina_html]['filtros']]:
                    filtrar_filtros += f'<li><a style="cursor:pointer;" title="Clique para adicionar ao mesmo filtro" onclick="$(\'#nome_pesquisa,#nome_pesquisa_sel\').val($(this).children(nome).text());"><span id="nome">{pagina[0]}</a> ({pagina[1]})</li>'
                    pagina_filtros += f'<li><a style="cursor:pointer;" target="_blank" href=\'../../cgi-bin/filtrar.cgi?action=view&html={pagina_html}&filtro=' + encodeUrl(pagina[0]) + f'\'>{pagina[0]} ({pagina[1]})</li>'
            else:
                filtros = []

    if os.path.isfile('../cgi-bin/json/' + slugify(conllu + "_" + parametros + ".json")):
        with open("../cgi-bin/json/" + slugify(conllu + "_" + parametros + ".json"), "r") as f:
            resultadosBusca = json.load(f)
    else:
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

    sent_id_list = []
    if 'sent_id_list' in form and form['sent_id_list'].value:
        sent_id_list = [re.sub(r'<.*?>', '', re.findall(r'# sent_id = (.*?)\n', x['resultado'])[0]) for x in resultadosBusca['output']]
        sent_id_list = [x for x in sent_id_list if x not in filtros]

    numeroOcorrencias = len(resultadosBusca['output']) - len(filtros)
    #numeroOcorrenciasMenosFiltro = numeroOcorrencias - len(filtros)
    if numeroOcorrencias > startPoint + 21 and numeroOcorrencias >= 1:
        finalPoint = startPoint + 20
        noMore = False
    else:
        finalPoint = len(resultadosBusca['output']) - len(filtros) + len(filtros)
        noMore = True

    arquivoHtml = ""
    resultados = []
    quantos = 0
    filtrado = int(form['filtrado'].value)
    for ocorrencia in resultadosBusca['output'][startPoint:]:
        anotado = estrutura_ud.Sentence(recursivo=False)
        estruturado = estrutura_ud.Sentence(recursivo=False)
        anotado.build(cgi.escape(ocorrencia['resultado'].replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<font color=' + tabela['yellow'] + '>', '@YELLOW/').replace('<font color=' + tabela['red'] + '>', '@RED/').replace('<font color=' + tabela['cyan'] + '>', '@CYAN/').replace('<font color=' + tabela['blue'] + '>', '@BLUE/').replace('<font color=' + tabela['purple'] + '>', '@PURPLE/').replace('</font>', '/FONT')))	
        estruturado.build(web.unescape(ocorrencia['resultado']).replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<font color=' + tabela['yellow'] + '>', '@YELLOW/').replace('<font color=' + tabela['red'] + '>', '@RED/').replace('<font color=' + tabela['cyan'] + '">', '@CYAN/').replace('<font color=' + tabela['blue'] + '>', '@BLUE/').replace('<font color=' + tabela['purple'] + '>', '@PURPLE/').replace('</font>', '/FONT').replace('@BOLD', '').replace('/BOLD', '').replace('@YELLOW/', '').replace('@RED/', '').replace('@CYAN/', '').replace('@BLUE/', '').replace('@PURPLE/', '').replace('/FONT', ''))

        if not estruturado.sent_id in filtros and not estruturado.text in filtros:
            resultados.append({'anotado': anotado, 'estruturado': estruturado})
            quantos += 1
        else:
            quantos += 1
            filtrado += 1
            if finalPoint+1 < len(resultadosBusca['output']):
                finalPoint += 1

        if quantos == finalPoint-startPoint:
            break

    for i, ocorrencia in enumerate(resultados):
        anotado = ocorrencia['anotado']
        estruturado = ocorrencia['estruturado']

        arquivoHtml += '<div class=container>\n'
        arquivoHtml += f'<p>{str(startPoint+i+1-filtradoPrevious)}/{numeroOcorrencias}</p>' + '\n'
        if estruturado.sent_id:
            arquivoHtml += '<p onmouseover="$(this).css(\'text-decoration\', \'underline\');" onmouseleave="$(this).css(\'text-decoration\', \'none\');" style="cursor:pointer;" class="metadados_sentence">'
            arquivoHtml += f'''<input class="cb translateTitle" id=checkbox_{str(startPoint+i+1)} style="margin-left:0px;" title="Selecionar sentença para filtragem" sent_id="{estruturado.sent_id}" type=checkbox>''' if nomePesquisa not in fastSearch else ""
            arquivoHtml += f'''{estruturado.sent_id}</p>''' + '\n'
        arquivoHtml += f"<p><span id=text_{str(startPoint+i+1)}>{(anotado.metadados['clean_text'] if 'clean_text' in anotado.metadados else anotado.text).replace('/BOLD', '</b>').replace('@BOLD', '<b>').replace('@YELLOW/', '<font color=' + tabela['yellow'] + '>').replace('@PURPLE/', '<font color=' + tabela['purple'] + '>').replace('@BLUE/', '<font color=' + tabela['blue'] + '>').replace('@RED/', '<font color=' + tabela['red'] + '>').replace('@CYAN/', '<font color=' + tabela['cyan'] + '>').replace('/FONT', '</font>')}</span></p>" + '\n'
        if ((estruturado.sent_id and ('-' in estruturado.sent_id or re.search(r'^\d+$', estruturado.sent_id))) or estruturado.id) and estruturado.text:
            arquivoHtml += f"<p><button class='translateHtml sentence-control' id=contexto_{str(startPoint+i+1)} onclick=\"contexto('{estruturado.sent_id}', '{estruturado.id}', '{corpus}')\" style=\"margin-left:0px\">Mostrar contexto</button> <button class='translateHtml anotacao sentence-control' id=mostrar_{str(startPoint+i+1)} onclick=\"mostrar('div_{str(startPoint+i+1)}', 'mostrar_{str(startPoint+i+1)}')\" style=\"margin-left:0px\">Mostrar anotação</button> <button class='translateHtml opt sentence-control' id=opt_{str(startPoint+i+1)} onclick=\"mostraropt('optdiv_{str(startPoint+i+1)}', 'opt_{str(startPoint+i+1)}')\" style=\"margin-left:0px\">Mostrar opções</button> <button class=\"abrirInquerito translateHtml sentence-control\" onclick='inquerito(\"form_{str(startPoint+i+1)}\"); $(this).css(\"background-color\", \"lightgray\");'>Abrir inquérito</button></p>" + "\n"
        else:
            arquivoHtml += f"<p><button id=mostrar_{str(startPoint+i+1)} class=\"translateHtml anotacao sentence-control\" onclick=\"mostrar('div_{str(startPoint+i+1)}', 'mostrar_{str(startPoint+i+1)}')\" style=\"margin-left:0px\">Mostrar anotação</button> <button id=opt_{str(startPoint+i+1)} class=\"translateHtml sentence-control opt\" onclick=\"mostraropt('optdiv_{str(startPoint+i+1)}', 'opt_{str(startPoint+i+1)}')\" style=\"margin-left:0px\">Mostrar opções</button> <button class='translateHtml' onclick='inquerito(\"form_{str(startPoint+i+1)}\")'>Abrir inquérito</button></p>" + '\n'
        arquivoHtml += f"<span style=\"display:none; padding-left:20px;\" id=\"optdiv_{str(startPoint+i+1)}\">"
        arquivoHtml += f"<form action=\"../../cgi-bin/inquerito.py?conllu={conllu}\" target=\"_blank\" method=POST id=form_{str(startPoint+i+1)}><input type=hidden name=sentid value=\"{estruturado.sent_id}\"><input type=hidden name=occ value=\"{numeroOcorrencias}\"><input type=hidden name=textheader value=\"{estruturado.text}\"><input type=hidden name=nome_interrogatorio value=\"{cgi.escape(nomePesquisa)}\"><input type=hidden name=link_interrogatorio value=\"{caminhoCompletoHtml}\">"
        if "@BOLD" in anotado.to_str():
            arquivoHtml += f"<input type=hidden name=tokenId value=\"" + "".join([functions.cleanEstruturaUD(x.id) for x in anotado.tokens if '@BOLD' in x.to_str()]) + "\">"
        arquivoHtml += "</form>"
        if nomePesquisa not in fastSearch: arquivoHtml += f"<!--a style=\"cursor:pointer\" onclick='filtraragora(\"{str(startPoint+i+1)}\")'>Separar sentença</a-->"
        #arquivoHtml += '<br>'
        arquivoHtml += f"<form action=\"../../cgi-bin/udpipe.py?conllu={conllu}\" target=\"_blank\" method=POST id=udpipe_{str(startPoint+i+1)}><input type=hidden name=textheader value=\"{estruturado.text}\"></form><a style=\"cursor:pointer\" onclick='anotarudpipe(\"udpipe_{str(startPoint+i+1)}\")' class='translateHtml'>Anotar frase com o UDPipe</a>"
        arquivoHtml += '<br>'
        arquivoHtml += f"<form action=\"../../cgi-bin/draw_tree.py?conllu={conllu}\" target=\"_blank\" method=POST id=tree_{str(startPoint+i+1)}><input type=hidden name=sent_id value=\"{estruturado.sent_id}\"><input type=hidden name=text value=\"{estruturado.text}\"></form><a style=\"cursor:pointer\" onclick='drawtree(\"tree_{str(startPoint+i+1)}\")' class='translateHtml'>Visualizar árvore de dependências</a>"
        arquivoHtml += '</p></span>\n'
        arquivoHtml += f"<pre id=div_{str(startPoint+i+1)} style=\"display:none\">{anotado.to_str().replace('/BOLD', '</b>').replace('@BOLD', '<b>').replace('@YELLOW/', '<font color=' + tabela['yellow'] + '>').replace('@PURPLE/', '<font color=' + tabela['purple'] + '>').replace('@BLUE/', '<font color=' + tabela['blue'] + '>').replace('@RED/', '<font color=' + tabela['red'] + '>').replace('@CYAN/', '<font color=' + tabela['cyan'] + '>').replace('/FONT', '</font>')}</pre>" + '\n'
        arquivoHtml += '</div>\n'

    print(json.JSONEncoder().encode({
            'success': True,
            'html': arquivoHtml,
            'noMore': noMore,
            'indexSentences': finalPoint,
            'filtrado': filtrado,
            'filtrar_filtros': filtrar_filtros,
            'pagina_filtros': pagina_filtros,
            'filtros': len(filtros),
            'sent_id_list': "|".join(sent_id_list),
            'sent_id_count': str(len(sent_id_list))
        }))

if os.environ['REQUEST_METHOD'] == "POST":
    if not 'ud' in form:
        start = time.time()
        renderSentences()
        sys.stderr.write('\nrenderSentences: ' + str(time.time() - start))
    else:
        loadCorpus(form['ud'].value, form['size'].value, form['updateCorpus'].value if 'updateCorpus' in form else False)
