#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

fastSearch = ['teste', 'Busca rápida']

print("Content-type:application/json; charset=utf-8")
print('\n\n')

import os
import cgi, cgitb
import shutil
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
import shutil

form = cgi.FieldStorage()

def loadCorpus(ud, size="0.0", updateCorpus=False):
    
    conllus = {}
    if os.path.isfile("./interrogar-ud/conllu.json"):
        with open("./interrogar-ud/conllu.json") as f:
            conllus = json.load(f)

    n_sent = 0
    n_tokens = 0
    n_files = 0
    files = []

    if (updateCorpus) or (size and float(size) < 50.0) or (ud in conllus):
        try:
            if not ud in conllus or updateCorpus:
                conllus[ud] = {}
                with open("./interrogar-ud/conllu/" + ud) as f:
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
                with open("./interrogar-ud/conllu.json", "w") as f:
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
    caminhoCompletoConllu = './interrogar-ud/conllu/' + conllu
    caminhoCompletoHtml = form['html'].value

    parametros = form['parametros'].value
    #if len(parametros.split('"')) > 2 or any(x in parametros for x in ["==", " = ", " != "]) or "tokens=" in parametros:
        #criterio = '5'
    #else:
        #criterio = '1'

    #if "script" in form:
        #script = form['script'].value

    startPoint = int(form['indexSentences'].value)
    filtradoPrevious = int(form['filtrado'].value) if 'filtrado' in form else 0
    nomePesquisa = form['nomePesquisa'].value
    json_id = form['jsonId'].value

    filtros = []
    filtrar_filtros = ""
    pagina_filtros = ""
    if nomePesquisa not in fastSearch:
        pagina_html = caminhoCompletoHtml.rsplit("/", 1)[1].rsplit(".", 1)[0]
        if os.path.isfile("./cgi-bin/filtros.json"):
            with open("./cgi-bin/filtros.json") as f:
                filtros_json = json.load(f)
            filtrar_filtros = "<h4 class='translateHtml'>Filtros já aplicados:</h4>" if pagina_html in filtros_json and filtros_json[pagina_html]['filtros'] else ""
            if pagina_html in filtros_json:
                filtros = [x for nome in filtros_json[pagina_html]['filtros'] for x in filtros_json[pagina_html]['filtros'][nome]['sentences']]
                for pagina in [[x, len(filtros_json[pagina_html]['filtros'][x]['sentences'])] for x in filtros_json[pagina_html]['filtros']]:
                    filtrar_filtros += f'<li><a style="cursor:pointer;" class="translateTitle" title="Clique para adicionar ao mesmo filtro" onclick="$(\'#nome_pesquisa,#nome_pesquisa_sel\').val($(this).children(nome).text());"><span id="nome">{pagina[0]}</a> ({pagina[1]})</li>'
                    pagina_filtros += f'<li><a style="cursor:pointer;" target="_blank" href=\'../../cgi-bin/filtrar.py?action=view&html={pagina_html}&filtro=' + encodeUrl(pagina[0]) + f'\'>{pagina[0]} ({pagina[1]})</li>'
            else:
                filtros = []

    #if os.path.isfile('./cgi-bin/json/' + json_id + ".json"):
    with open("./cgi-bin/json/" + json_id + ".json", "r") as f:
        resultadosBusca = json.load(f)
    #else:
        #if not script:
        #resultadosBusca = interrogar_UD.main(caminhoCompletoConllu, criterio, parametros)
        #else:
            #shutil.copy("./cgi-bin/scripts/" + script, './cgi-bin/queryScript.py')
            #with open("./cgi-bin/queryScript.py", 'r') as f:
                #scriptFile = f.read().replace("<!--corpus-->", caminhoCompletoConllu)
            #with open("./cgi-bin/queryScript.py", "w") as f:
                #f.write(scriptFile)
            #import queryScript
            #resultadosBusca = queryScript.getResultadosBusca()

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
        anotado.build(web.escape(ocorrencia['resultado'].replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<font color=' + tabela['yellow'] + '>', '@YELLOW/').replace('<font color=' + tabela['red'] + '>', '@RED/').replace('<font color=' + tabela['cyan'] + '>', '@CYAN/').replace('<font color=' + tabela['blue'] + '>', '@BLUE/').replace('<font color=' + tabela['purple'] + '>', '@PURPLE/').replace('</font>', '/FONT')))	
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

        arquivoHtml += '<div class="container sentence-container">\n'
        arquivoHtml += f'<p>{str(startPoint+i+1-filtradoPrevious)}/{numeroOcorrencias}</p>' + '\n'
        if estruturado.sent_id:
            arquivoHtml += '<p {} class="metadados_sentence">'.format('onmouseover="$(this).css(\'text-decoration\', \'underline\');" onmouseleave="$(this).css(\'text-decoration\', \'none\');"' if nomePesquisa not in fastSearch else "")
            arquivoHtml += f'''<input class="cb translateTitle" id=checkbox_{str(startPoint+i+1)} style="margin-left:0px;" title="Selecionar sentença para filtragem" sent_id="{estruturado.sent_id}" type=checkbox>''' if nomePesquisa not in fastSearch else ""
            arquivoHtml += f'''{estruturado.sent_id}</p>''' + '\n'
        arquivoHtml += f"<p><span id=text_{str(startPoint+i+1)}>{(anotado.metadados['clean_text'] if 'clean_text' in anotado.metadados else anotado.text).replace('/BOLD', '</b>').replace('@BOLD', '<b>').replace('@YELLOW/', '<font color=' + tabela['yellow'] + '>').replace('@PURPLE/', '<font color=' + tabela['purple'] + '>').replace('@BLUE/', '<font color=' + tabela['blue'] + '>').replace('@RED/', '<font color=' + tabela['red'] + '>').replace('@CYAN/', '<font color=' + tabela['cyan'] + '>').replace('/FONT', '</font>')}</span></p>" + '\n'
        if ((estruturado.sent_id and ('-' in estruturado.sent_id or re.search(r'^\d+$', estruturado.sent_id))) or estruturado.id) and estruturado.text:
            arquivoHtml += f"<p class='toolbar' <!--style='display:none;'--><button class='translateHtml sentence-control' id=contexto_{str(startPoint+i+1)} onclick=\"contexto('{estruturado.sent_id}', '{estruturado.id}', '{corpus}')\" style=\"margin-left:0px\">Mostrar contexto</button> <button class='translateHtml anotacao sentence-control' id=mostrar_{str(startPoint+i+1)} onclick=\"mostrar('div_{str(startPoint+i+1)}', 'mostrar_{str(startPoint+i+1)}')\" style=\"margin-left:0px\">Mostrar anotação</button> <button class='translateHtml opt sentence-control' id=opt_{str(startPoint+i+1)} onclick=\"mostraropt('optdiv_{str(startPoint+i+1)}', 'opt_{str(startPoint+i+1)}')\" style=\"margin-left:0px\">Mostrar opções</button> <button class=\"abrirInquerito translateHtml sentence-control\" onclick='inquerito(\"form_{str(startPoint+i+1)}\");'>Abrir inquérito</button></p>" + "\n"
        else:
            arquivoHtml += f"<p class='toolbar' <!--style='display:none;'--><button id=mostrar_{str(startPoint+i+1)} class=\"translateHtml anotacao sentence-control\" onclick=\"mostrar('div_{str(startPoint+i+1)}', 'mostrar_{str(startPoint+i+1)}')\" style=\"margin-left:0px\">Mostrar anotação</button> <button id=opt_{str(startPoint+i+1)} class=\"translateHtml sentence-control opt\" onclick=\"mostraropt('optdiv_{str(startPoint+i+1)}', 'opt_{str(startPoint+i+1)}')\" style=\"margin-left:0px\">Mostrar opções</button> <button class='translateHtml abrirInquerito sentence-control' onclick='inquerito(\"form_{str(startPoint+i+1)}\")'>Abrir inquérito</button></p>" + '\n'
        arquivoHtml += f"<span style=\"display:none; padding-left:20px;\" id=\"optdiv_{str(startPoint+i+1)}\">"
        arquivoHtml += f"<form action=\"../../cgi-bin/inquerito.py?conllu={conllu}\" target=\"_blank\" method=POST id=form_{str(startPoint+i+1)}><input type=hidden name=sentid value=\"{estruturado.sent_id}\"><input type=hidden name=occ value=\"{numeroOcorrencias}\"><input type=hidden name=textheader value=\"{estruturado.sent_id}\"><input type=hidden name=nome_interrogatorio value=\"{web.escape(nomePesquisa)}\"><input type=hidden name=link_interrogatorio value=\"{caminhoCompletoHtml}\"><input type=hidden name=text value=\"{estruturado.text}\">"
        if "@BOLD" in anotado.to_str():
            arquivoHtml += f"<input type=hidden name=tokenId value=\"" + ",".join([functions.cleanEstruturaUD(x.id) for x in anotado.tokens if '@BOLD' in x.to_str()]) + "\">"
        arquivoHtml += "</form><br>"
        if nomePesquisa not in fastSearch: arquivoHtml += f"<a style=\"cursor:pointer\" onclick='selectAbove({str(startPoint+i+1)})' class='translateHtml'>Selecionar todas as frases acima</a><br>"
        if nomePesquisa not in fastSearch: arquivoHtml += f"<!--a style=\"cursor:pointer\" onclick='filtraragora(\"{str(startPoint+i+1)}\")'>Separar sentença</a-->"
        #arquivoHtml += '<br>'
        if nomePesquisa in fastSearch: arquivoHtml += "<span class='translateHtml'>Salve a busca para liberar mais opções</span>"
        arquivoHtml += f"<form action=\"../../cgi-bin/udpipe.py?conllu={conllu}\" target=\"_blank\" method=POST id=udpipe_{str(startPoint+i+1)}><input type=hidden name=textheader value=\"{estruturado.text}\"></form><!--a style=\"cursor:pointer\" onclick='anotarudpipe(\"udpipe_{str(startPoint+i+1)}\")' class='translateHtml'>Anotar frase com o UDPipe</a!-->"
        arquivoHtml += ''
        arquivoHtml += f"<form action=\"../../cgi-bin/draw_tree.py?conllu={conllu}\" target=\"_blank\" method=POST id=tree_{str(startPoint+i+1)}><input type=hidden name=sent_id value=\"{estruturado.sent_id}\"><input type=hidden name=text value=\"{estruturado.text}\"></form><!--a style=\"cursor:pointer\" onclick='drawtree(\"tree_{str(startPoint+i+1)}\")' class='translateHtml'>Visualizar árvore de dependências</a-->"
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

def delete_sentence(filename, sent_id):
    corpus = estrutura_ud.Corpus(recursivo=False, sent_id=sent_id)
    corpus.load("./interrogar-ud/conllu/" + filename)
    del corpus.sentences[sent_id]
    corpus.save("./interrogar-ud/conllu/" + filename)
    return True

def modify_sentid(filename, sent_id, new_sentid):
    corpus = estrutura_ud.Corpus(recursivo=False, sent_id=sent_id)
    corpus.load("./interrogar-ud/conllu/" + filename)
    corpus.sentences[sent_id].sent_id = new_sentid
    corpus.sentences[sent_id].metadados['sent_id'] = new_sentid
    corpus.sentences[new_sentid] = corpus.sentences.pop(sent_id)
    corpus.save("./interrogar-ud/conllu/" + filename)
    return True

def generate_query_script(query="", save_openai_key=False):
    openai_key_file = "./cgi-bin/openai_key.txt"
    if not save_openai_key:
        try:
            import openai

            if os.path.isfile(openai_key_file):
                with open(openai_key_file) as f:
                    openai.api_key = f.read().strip()
            else:
                return "NO API KEY FOUND"

            prompt = [
                {"role": "user", "content": '''
                    Build a Python code that will query through the tokens in a sentence to search for specific sentences.
                    The sentence is morphosyntactically annotated in the Universal Dependences format.
                    The list of tokens in a sentence can be accessed from "sentence.tokens", and you will have to iterate through the tokens in this list to find the correct ones.
                    The first line of the code (not counting possible comments) should be "for token in sentence.tokens:"
                    The tokens that fulfill the user's condition should be added to the list "bold_tokens". DO NOT initialize this list, nor make any comments about it, we are assuming it is already initialized elsewhere in the full code.
                    Each token has the attributes "token.head_token", "token.previous_token" and "token.next_token", which return the corresponding tokens, along with the attributes "id", "word", "lemma", "upos", "xpos", "dephead", "deprel", "deps", and "misc", according to the Universal Dependencies annotation.
                    
                    Here is an example of code generated from user input:
                                   
                    if token.deprel == "expl:pv":
                        verb = token.head_token
                        has_subject = False
                        for _token in sentence.tokens:
                            if _token.dephead == verb.id and _token.deprel.startswith("nsubj"):
                                has_subject = True
                                break
                        if not has_subject:
                            bold_tokens.append(token)
                '''},
                {"role": "system", "content": "Sure, tell me what token you want to look for in a sentence and I will generate a Python code (with comments in each line written in your language) that performs this query. I will not write anything besides the code block itself."},
            ]
            
            prompt.append({'role': 'user', 'content': query})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=prompt,
            )

            response = response['choices'][0]['message']['content']

            if '```python' in response:
                response = response.split("```python")[1].split("```")[0].strip()

            # para fine-tuning quando tiver exemplos suficientes (lembrar de traduzir português/inglês usando o próprio gpt)
            with open("./cgi-bin/chatGPTQueryScriptRecord.jsonl", "a") as f:
                f.write(json.dumps({'prompt': query, 'completion': response}, ensure_ascii=False) + "\n")

            return "# This script was generated by an AI and may contain errors.\n# Please revise it if needed.\n\n" + response
        
        except Exception as e:
            return str(e)
    else:
        with open(openai_key_file, "w") as f:
            f.write(save_openai_key.strip())

if os.environ.get('REQUEST_METHOD') == "POST":
    if 'action' in form and form['action'].value == "generate_query_script":
        code = generate_query_script(query=form['query'].value)
        with open("./interrogar-ud/chatGPTQueryScript.txt", "w") as f:
            f.write(code)
        print(json.JSONEncoder().encode({'success': True, 'code': code}))
    elif 'action' in form and form['action'].value == "save_openai_key":
        generate_query_script(save_openai_key=form['openai_key'].value)
        print(json.JSONEncoder().encode({'success': True}))
    elif 'action' in form and form['action'].value == "delete_sentence":
        delete_sentence(form['corpus'].value, form['sent_id'].value)
        print(json.JSONEncoder().encode({'success': True}))
    elif 'action' in form and form['action'].value == 'modify_sentid':
        modify_sentid(form['corpus'].value, form['sent_id'].value, form['new_sentid'].value)
        print(json.JSONEncoder().encode({'success': True}))
    elif not 'ud' in form:
        start = time.time()
        renderSentences()
        sys.stderr.write('\nrenderSentences: ' + str(time.time() - start))
    else:
        loadCorpus(form['ud'].value, form['size'].value, form['updateCorpus'].value if 'updateCorpus' in form else False)
else:
    if sys.argv[1] == "generate_query_script":
        if len(sys.argv) != 3:
            query = "Find pronouns with lemma \"se\" which are dependent on verbs which do not have any subject dependent on them."
        else:
            query = sys.argv[2]
        print(generate_query_script(query=query))