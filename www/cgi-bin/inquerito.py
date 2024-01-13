#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print('Content-type:text/html; charset=utf-8')
print('\n\n')

import sys
import cgi, cgitb
cgitb.enable()
import time
import estrutura_dados
import pandas as pd
import uuid
import os
import shutil
from datetime import datetime
from utils import corpusGenericoInquerito, fastsearch, cleanEstruturaUD, idx_to_col, build_modifications_html
import re
import html as web
import subprocess
import html as web
import validar_UD
from credenciar import LOGIN
import interrogar_UD
import variables
from udapi.core.document import Document
from io import StringIO
import json

JULGAMENTO = False
if os.path.isdir("../Julgamento"):
    JULGAMENTO = "../Julgamento"
if os.path.isdir("../../Julgamento"):
    JULGAMENTO = "../../Julgamento"

def draw_tree(conllu):
    """Test the draw() method, which uses udapi.block.write.textmodetrees."""
    with RedirectedStdout() as out:
        doc = Document()
        data_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), conllu)
        doc.load_conllu([data_filename])
        root = doc.bundles[0].get_tree()
        root.draw(indent=4, color=False, attributes='form,upos,deprel',
                    print_sent_id=False, print_text=False, print_doc_meta=False)
        s = str(out)
    return s

class RedirectedStdout:
    def __init__(self):
        self._stdout = None
        self._string_io = None

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._string_io = StringIO()
        return self

    def __exit__(self, type, value, traceback):
        sys.stdout = self._stdout

    def __str__(self):
        return self._string_io.getvalue()

form = cgi.FieldStorage()

if not os.path.isdir("./interrogar-ud/inqueritos"):
	os.mkdir("./interrogar-ud/inqueritos")

# Backwards compatibility
if os.path.isfile("./interrogar-ud/inqueritos.txt"):
	new_inquiries = []
	with open("./interrogar-ud/inqueritos.txt") as f:
		inqueritos = f.read().splitlines()
	for inquerito in inqueritos:
		_id = str(uuid.uuid4())
		if inquerito.strip():
			new_inquiries.append({
				'_id': _id,
				'date': datetime.strptime(inquerito.split("!@#")[3], '%Y-%m-%d_%H:%M:%S').timestamp(),
				'text': inquerito.split("!@#")[0],
				'before': inquerito.split("!@#")[1].split(" --> ")[0],
				'after': inquerito.split("!@#")[1].split(" --> ")[1].split(" (head: ")[0],
				'head': inquerito.split("!@#")[1].split(" --> ")[1].split(" (head: ")[1].split(")")[0] if "head:" in inquerito else None,
				'conllu': inquerito.split("!@#")[2].split(".conllu")[0],
				'interrogatorio': inquerito.split("!@#")[4].rsplit(" (", 1)[0] if inquerito.split("!@#")[4] != "NONE" else None,
				'occurrences': inquerito.split("!@#")[4].rsplit(" (", 1)[1].split(")")[0] if inquerito.split("!@#")[4] != "NONE" else None,
				'href': inquerito.split("!@#")[5] if inquerito.split("!@#")[4] != "NONE" else None,
				'tag': inquerito.split("!@#")[6] if inquerito.split("!@#")[6] != "NONE" else None,
				'sent_id': inquerito.split("!@#")[7]
			})
	
	df = pd.DataFrame(new_inquiries)
	_ids = df._id.unique()
	for _id in _ids:
		rows = df[df._id == _id]
		filename = "./interrogar-ud/inqueritos/%s.csv" % _id
		rows.to_csv(filename)
	os.remove("./interrogar-ud/inqueritos.txt")

bosqueNaoEncontrado = corpusGenericoInquerito

arquivos = list()
for i, arquivo in enumerate(os.listdir('./interrogar-ud/conllu')):
	arquivos.append('<option value="'+arquivo+'">'+arquivo+'</option>')

with open('./interrogar-ud/inquerito.html', 'r') as f:
	html = f.read()
html = html.split('<select name="conllu">')[0] + '<select name="conllu">' + "\n".join(arquivos) + '</select>' + html.split('</select>')[1]

html1 = html.split('<!--SPLIT-->')[0]
html2 = html.split('<!--SPLIT-->')[1]

def get_head(frase, token):
	if token[7] == '0':
		return '_'
	for linha in frase:
		if isinstance(linha, list) and token[6] == linha[0]:
			return linha[1]
	return ''

if (os.environ['REQUEST_METHOD'] == "POST") or ('textheader' in cgi.FieldStorage() and 'corpus' in cgi.FieldStorage()):
	if LOGIN:
		if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
			html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
			print(html)
			exit()
	else:
		pass

if os.environ['REQUEST_METHOD'] == "POST" and 'ud' in form.keys() and 'action' in form.keys() and form['action'].value == 'apagarCorpus':
	shutil.move('./interrogar-ud/conllu/' + form['ud'].value, './interrogar-ud/tmp/' + form['ud'].value)
	if JULGAMENTO and os.path.isfile(f'{JULGAMENTO}/static/uploads/' + form['ud'].value.rsplit(".", 1)[0] + "_original.conllu"):
		os.remove(f'{JULGAMENTO}/static/uploads/' + form['ud'].value.rsplit(".", 1)[0] + "_original.conllu")
	print('<script>window.location = "../cgi-bin/arquivo_ud.py"</script>')
	exit()

elif os.environ['REQUEST_METHOD'] == 'POST' and 'action' in form.keys() and form['action'].value == 'script':
	nome_interrogatorio = form['nome_interrogatorio'].value
	link_interrogatorio = form['link_interrogatorio'].value.rsplit(".", 1)[0].rsplit("/", 1)[1]

	filtros = []
	if os.path.isfile("./cgi-bin/json/filtros.json"):
		with open("./cgi-bin/json/filtros.json") as f:
			filtros = json.load(f)
		if link_interrogatorio in filtros:
			filtros = [x for filtro in filtros[link_interrogatorio]['filtros'] for x in filtros[link_interrogatorio]['filtros'][filtro]['sentences']]
		else:
			filtros = []

	start = time.time()
	headers = list()
	for sentence in interrogar_UD.main('./interrogar-ud/conllu/' + form['conllu'].value, int(form['criterio'].value), form['parametros'].value, fastSearch=True)['output']:
		sent_id = re.sub(r"<.*?>", "", sentence['resultado'].split("# sent_id = ")[1].split("\n")[0])
		if not sent_id in filtros:
			headers.append(sent_id)
	sys.stderr.write('\nheaders: {}'.format(time.time() - start))

	if form['executar'].value == 'sim':
		with open('./interrogar-ud/scripts/' + estrutura_dados.slugify(form['scriptName'].value), 'wb') as f:
			code = form['fileScript'].file.read()
			f.write(code)

	with open('./interrogar-ud/scripts/headers.txt', 'w') as f:
		f.write("\n".join(headers))
	
	start = time.time()
	call_python = "python3" if not 'win' in sys.platform else os.path.join("..", "Python39", "python.exe")
	command = [
		f'{call_python}',
		f'./interrogar-ud/scripts/batch_correction.py',
		f'{form["conllu"].value}',
		f'{form["executar"].value}',
		f'{estrutura_dados.slugify(form["scriptName"].value)}',
		f'{form["scriptName"].value}',
		f'{form["nome_interrogatorio"].value}',
		f'{form["occ"].value}',
		f'{form["link_interrogatorio"].value}',
		f'{form["parametros"].value}',
		f'{form["fullParameters"].value}',
		]
	
	if 'win' in sys.platform:
		subprocess.call(command, shell=True)
	else:
		subprocess.run(command)
	sys.stderr.write('\nbatch_correction: {}'.format(time.time() - start))
	
	if form['executar'].value == 'exec':
		df = pd.read_csv("./interrogar-ud/batch_correction_simulation.csv", index_col=0)
		_id = df._id.iloc[0]
		os.rename("./interrogar-ud/batch_correction_simulation.csv", "./interrogar-ud/inqueritos/%s.csv" % (_id))
		os.remove('./interrogar-ud/conllu/' + form['conllu'].value)
		os.rename('./interrogar-ud/conllu/' + form['conllu'].value + '_script', './interrogar-ud/conllu/' + form['conllu'].value)
		html = f"<script>window.alert('Modificações realizadas com sucesso!'); window.location.href = '../cgi-bin/relatorio.py?id={_id}'</script>"
					
	elif form['executar'].value == 'sim':
		try:
			df = pd.read_csv("./interrogar-ud/batch_correction_simulation.csv", index_col=0)
			os.remove("./interrogar-ud/batch_correction_simulation.csv")
		except:
			with open("./cgi-bin/debug_batch_correction_error.log", "r") as f:
				file_errors = f.read()
			os.remove("./cgi-bin/debug_batch_correction_error.log")
			print(file_errors.splitlines()[-1])
			exit()

		if (len(df)):
			_id = df._id.iloc[0]
		else:
			print("A regra de correção não encontrou nenhuma correspondência nas frases ou nenhuma modificação seria realizada com as condições do script.")
			exit()

		html = f'<title>Simulação de correção em lote: Interrogatório</title><h1>Simulação de correção em lote ({len(df)})</h1>Essa página é apenas uma simulação das alterações que serão feitas no corpus.'
		html += '<br>Verifique se as alterações estão adequadas e execute o script de correção no <a style="color:blue; cursor:pointer;" onclick="window.scrollTo(0,document.body.scrollHeight);">final da página</a>.'
		html += "<hr>"
		html += build_modifications_html(df, _id)
		html += '<hr>Clique se a simulação estiver adequada para executar o script, salvar as modificações e visualizar o relatório de modificações (inquéritos):'
		html += '<br><br>'
		html += '<form action="../cgi-bin/inquerito.py?action=script&executar=exec" id="execScriptForm" method="POST">'
		html += '<input type=hidden name=parametros value=\''+form['parametros'].value+'\'>'
		html += '<input type=hidden name=fullParameters value=\''+form['fullParameters'].value+'\'>'
		html += '<input type=hidden name=criterio value=\"'+form['criterio'].value+'\">'
		html += '<input type=hidden name="nome_interrogatorio" value="' + form['nome_interrogatorio'].value.replace('"', '&quot;') + '">'
		html += '<input type=hidden name=occ value="' + form['occ'].value + '">'
		html += '<input type=hidden name="link_interrogatorio" value="' + form['link_interrogatorio'].value + '">'
		html += '<input type=hidden name="conllu" value="' + form['conllu'].value + '">'
		html += '<input type=hidden value="' + form['scriptName'].value.replace('"', '&quot;') + '" name="scriptName">'
		html += '<input type=submit value="EXECUTAR SCRIPT" id="execScript" onclick="execScript.value = \'AGUARDE...\'; execScript.disabled = true; execScriptForm.submit()"></form>'
		html += "<hr><br>"

	os.remove('./interrogar-ud/scripts/headers.txt')
	print(html)

elif ((os.environ['REQUEST_METHOD'] == 'POST') or ('conllu' in form and 'textheader' in form)) and ((not 'action' in form.keys()) or ((form['action'].value != 'alterar' and form['action'].value != 'script'))):
	html1 = html1.replace('<title class="translateHtml">Sistema de inquéritos</title>', '<title class="translateHtml">Novo inquérito: Interrogatório</title>') if not 'finalizado' in form else html1.replace('<title class="translateHtml">Sistema de inquéritos</title>', '<title class="translateHtml">Inquérito realizado com sucesso: Interrogatório</title>')
	ud = form['conllu'].value
	colored_ud = ud
	if not os.path.isfile('./interrogar-ud/conllu/' + ud):
		print(f"Corpus {ud} não encontrado.")
		exit()
	conlluzao = estrutura_dados.LerUD('./interrogar-ud/conllu/' + ud)
	if 'finalizado' in form:
		erros = []
		if 'sentid' in form:
			erros = validar_UD.validate('./interrogar-ud/conllu/' + ud, sent_id=form['sentid'].value, noMissingToken=True, errorList=variables.validar_UD)
		alertColor = "cyan" if not erros else "yellow"
		alertBut = "" if not erros else ", mas atenção:"
		html1 += f'<span style="background-color: {alertColor}"><span class="translateHtml">Alteração realizada com sucesso</span>{alertBut}</span>'
		if alertBut:
			html1 += "<ul>" 
			for erro in erros:
				html1 += f'<li>{erro}</li><ul>'
				for sentence in erros[erro]:
					if sentence and sentence['sentence']:
						html1 += f'''<li><a style="cursor:pointer" onclick="$('.id_{cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].id)}').focus();">{cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].id)} / {cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].word)}{' / ' + cleanEstruturaUD(sentence['sentence'].tokens[sentence['t']].__dict__[sentence['attribute']]) if sentence['attribute'] else ""}</a></li>'''
				html1 += "</ul>"
			html1 += "</ul>"
		html1 += '<br>'
	if 'tokenizado' in form:
		new_sentid = ""
		if form['tokenizado'].value != "True":
			new_sentid = form['tokenizado'].value
		if not new_sentid:
			html1 += f'<span style="background-color: cyan"><span class="translateHtml">Tokenização modificada com sucesso</span></span>'
		elif new_sentid:
			html1 += f'<span style="background-color: cyan"><span class="translateHtml">Tokenização modificada com sucesso</span></span><br><span style="background-color: yellow"><span class="translateHtml">Atenção: edite também o sent_id desta sentença e/ou a nova sentença:</span> <a href="../cgi-bin/inquerito.py?conllu={ud}&sentid={new_sentid}&textheader={new_sentid}" target="_blank">{new_sentid}</a></span>'
		html1 += "<br>"

	mostrar_contexto = f'<a href="../cgi-bin/contexto.py?corpus={ud}&sent_id={form["sentid"].value}" target="_blank" class="translateHtml">Mostrar contexto</a> - ' if 'sentid' in form and (('-' in form['sentid'].value and re.search('^\d+$', form['sentid'].value.rsplit("-", 1)[1])) or (re.search("^\d+$", form['sentid'].value))) else ""
	html1 = html1.split('<div class="header">')[0] + '<div class="header"><h1 class="translateHtml">Novo inquérito</h1><br><br>' + colored_ud + f'<br><br><a href="../cgi-bin/relatorio.py" class="translateHtml">Relatório de inquéritos</a> - ' + mostrar_contexto + ' <form style="display:inline-block" target="_blank" method="POST" action="../cgi-bin/draw_tree.py?conllu=' + ud + '"><!--a href="#" onclick="this.parentNode.submit()" class="translateHtml">Visualizar árvore</a--><input type=hidden name=text value="' + form['textheader'].value + '"><input type=hidden name=sent_id value="' + form['sentid'].value + '"></form><a style="cursor:pointer;" onclick="window.close()" class="translateHtml endInquerito">Encerrar inquérito</a></div>' + html1.split('</div>', 3)[3]

	achou = False
	for i, sentence in enumerate(conlluzao):
		sentence2 = sentence
		for a, linha in enumerate(sentence2):
			if isinstance(linha, list):
				sentence2[a] = '\t'.join(sentence2[a])
		sentence2 = '\n'.join(sentence2)
		if '# text = ' in form['textheader'].value or '# sent_id = ' in form['textheader'].value:
			form['textheader'].value = form['textheader'].value.split(' = ', 1)[1]
		if ('# text = ' + form['textheader'].value + '\n' in sentence2) or ('# sent_id = ' + form['textheader'].value + '\n' in sentence2) or ('sentid' in form and '# sent_id = ' + form['sentid'].value + '\n' in sentence2):
			html1 += '<h3 class="translateHtml">Controles:</h3><span class="translateHtml">Esc: Encerrar inquérito</span><br><span class="translateHtml">Tab / Shift + Tab: ir para coluna à direita/esquerda</span><br><span class="translateHtml">↑ / ↓: ir para linha acima/abaixo</span><br><span class="translateHtml">↖: Arraste a coluna <b>dephead</b> de um token para a linha do token do qual ele depende</span><br><span class="translateHtml">Shift + Scroll: Mover tabela para os lados</span><br><br>'
			html1 += '<input style="display: inline-block; margin: 0px; cursor:pointer;" type="button" onclick="enviar()" class="translateVal btn-gradient green small" id="sendAnnotation" value="Realizar alteração (Ctrl+Enter)"> '
			html1 += '<input style="display: inline-block; margin: 0px; cursor:pointer;" type="button" class="translateVal btn-gradient blue small" id="changeTokenization" value="Modificar tokenização"> '
			html1 += '<input style="display: inline-block; margin: 0px; cursor:pointer;" type="button" class="translateVal btn-gradient orange small" id="viewTree" value="Ver árvore"><br><br>'
			html1 += '<!--br><br><br-->'

			html1 += '''<div class="divTokenization" style="display:none">
			<b class="translateHtml">Escolha que modificação deseja realizar:</b>
			<ul>
				<li><a class="translateHtml tokenizationMenu" style="cursor:pointer" onclick="$('.tokenization').hide(); $('.addToken').show();">Adicionar ou remover token</a></li>
				<li><a class="translateHtml tokenizationMenu" style="cursor:pointer" onclick="$('.tokenization').hide(); $('.mergeSentences').show();">Mesclar duas sentenças</a></li>
				<li><a class="translateHtml tokenizationMenu" style="cursor:pointer" onclick="$('.tokenization').hide(); $('.splitSentence').show();">Separar sentença em duas</a></li>
				<li><a class="translateHtml tokenizationMenu" style="cursor:pointer" id="modifySentid" corpus="{corpus_plain}" sent_id="{sent_id_plain}">Modificar sent_id</a></li>
				<li><a class="translateHtml tokenizationMenu" style="cursor:pointer" id="deleteSentence" corpus="{corpus_plain}" sent_id="{sent_id_plain}">Deletar sentença</a></li>
			</ul>
			<div class="addToken tokenization" style="display:none">
				<form action="../cgi-bin/tokenization.py?action=addToken" class="addTokenForm" method="POST">
					<select name="addTokenOption" class="addTokenOption">
						<option value="add" class="addTokenOptionSelect translateHtml">Adicionar token</option>
						<option value="rm" class="addTokenOptionSelect translateHtml">Remover token</option>
						<option value="addContraction" class="addTokenOptionSelect translateHtml">Adicionar contração</option>
					</select>
					<span class="translateHtml addTokenHelp"> antes do token de id </span>
					<input class="translatePlaceholder" onkeyup="$('.addTokenButton').val($('.addTokenOptionSelect:selected').text() + $('.addTokenHelp').html() + $(this).val());" name="addTokenId">
					<input type="button" onclick="if ($('[name=addTokenOption]').val() && $('[name=addTokenId]').val()) {{ $('.addTokenForm').submit(); }}" class="translateVal addTokenButton" value="Adicionar token">
					<br><br><i><span class="translateHtml">Dicas:<br>Utilize vírgula para determinar mais de um id de token.<br>Utilize o sinal de maior ">" para indicar intervalo de id (por ex., "4>6" para "de 4 até 6")</span></i>
					{sentid}
					{link}
					{nome}
					{occ}
					{conllu}
					{tokenId}
					{sentnum}
					{textheader}
					{text}
				</form>
			</div>
			<div class="splitSentence tokenization" style="display:none">
				<form action="../cgi-bin/tokenization.py?action=splitSentence" class="splitSentenceForm" method="POST">
					<span class="translateHtml splitSentenceHelp">Separar sentença após o token de id </span>
					<input class="splitSentenceField" onkeyup="$('.splitSentenceButton').val('Separar sentença após o token de id ' + $(this).val());" name="splitSentenceTokenId">
					<br><br><span class="translateHtml splitSentenceHelp">Esta sentença terá seu sent_id modificado?</span>
					<input class="splitSentenceField" style="width:100%" value="{sent_id_plain}" name="sameSentenceId">
					<br><br><span class="translateHtml splitSentenceHelp">A nova sentença receberá qual sent_id?</span>
					<input class="splitSentenceField" style="width:100%" value="{sent_id_plain}-NEW" name="newSentenceId">
					<br><br><span class="translateHtml splitSentenceHelp">Esta sentença terá seu "text" modificado?</span>
					<input class="splitSentenceField" style="width:100%" value="{text_plain}" name="sameText">
					<br><br><span class="translateHtml splitSentenceHelp">A nova sentença receberá qual "text"?</span>
					<input class="splitSentenceField" style="width:100%" value="{text_plain}" name="newText">
					<br><br>
					<input type="button" onclick="if (!anySplitSentenceFieldEmpty()) {{ $('.splitSentenceForm').submit(); }}" class="translateVal splitSentenceButton" value="Separar sentença">
					<br><br>
					{sentid}
					{link}
					{nome}
					{occ}
					{conllu}
					{tokenId}
					{sentnum}
					{textheader}
					{text}
				</form>
			</div>
			<div class="mergeSentences tokenization" style="display:none">
				<form action="../cgi-bin/tokenization.py?action=mergeSentences" class="mergeSentencesForm" method="POST">
					<span class="translateHtml mergeSentencesHelp">Inserir sentença de sent_id </span> 
					<input style="width:250px;" class="translatePlaceholder" onkeyup="$('.mergeSentencesButton').val('Inserir sentença ' + $(this).val() + ' ' + $('.mergeSentencesOptionSelect:selected').text());" name="mergeSentencesId">
					<select name="mergeSentencesOption" onchange="$('.mergeSentencesButton').val('Inserir sentença ' + $('[name=mergeSentencesId]').val() + ' ' + $('.mergeSentencesSelect:selected').text());">
						<option value="right" class="mergeSentencesOptionSelect translateHtml">à direita</option>
						<option value="left" class="mergeSentencesOptionSelect translateHtml">à esquerda</option>
					</select>					
					<input type="button" onclick="if ($('[name=mergeSentencesOption]').val() && $('[name=mergeSentencesId]').val()) {{ $('.mergeSentencesForm').submit(); }}" class="translateVal mergeSentencesButton" value="Inserir sentença">
					<br><br><i><span class="translateHtml">Dica: Utilize vírgula para determinar mais de um sent_id.</span></i>
					{sentid}
					{link}
					{nome}
					{occ}
					{conllu}
					{tokenId}
					{sentnum}
					{textheader}
					{text}
				</form>
			</div>
			<span class="changesNotSaved translateHtml" style="background-color:yellow;"></span>
			</div>'''.format(
				sentid='<input type=hidden name=tokenization_sentid value="' + form['sentid'].value.replace('"', '&quot;') + '">' if 'sentid' in form else '',
				link='<input type=hidden name=tokenization_link_interrogatorio value="' + form['link_interrogatorio'].value + '">' if 'link_interrogatorio' in form and form['link_interrogatorio'].value not in fastsearch else '',
				nome='<input type=hidden name=tokenization_nome_interrogatorio value="' + form['nome_interrogatorio'].value.replace('"', '&quot;') + '">' if 'nome_interrogatorio' in form and form['nome_interrogatorio'].value not in fastsearch else '',
				occ='<input type=hidden name=tokenization_occ value="' + form['occ'].value + '">' if 'nome_interrogatorio' in form and form['nome_interrogatorio'].value not in fastsearch and 'occ' in form else '',
				conllu='<input type=hidden name=tokenization_conllu value="' + ud + '">',
				tokenId='<input type=hidden name=tokenization_tokenId value="' + form['tokenId'].value + '">' if 'tokenId' in form else '',
				sentnum='<input type=hidden name=tokenization_sentnum value="' + str(i) + '">' if 'sentnum' in form else '',
				textheader='<input type=hidden name=tokenization_textheader value="' + form['textheader'].value + '">' if 'textheader' in form else '',
				corpus_plain=ud,
				sent_id_plain=form['sentid'].value,
				text='<input type=hidden name=text value="' + form['text'].value.replace('"', '&quot;') + '">' if 'text' in form else '',
				text_plain=form['text'].value if 'text' in form else '',
			)

			html1 += '<form action="../cgi-bin/inquerito.py?sentnum='+str(i)+'&conllu=' + ud + '&action=alterar" id="dados_inquerito" method="POST">'
			if 'sentid' in form: html1 = html1 + '<input type=hidden name=sentid value="' + form['sentid'].value.replace('"', '\"') + '">'
			if 'link_interrogatorio' in form and form['link_interrogatorio'].value not in fastsearch:
				html1 = html1 + '<input type=hidden name=link_interrogatorio value="' + form['link_interrogatorio'].value + '">'
			if 'nome_interrogatorio' in form and form['nome_interrogatorio'].value not in fastsearch:
				html1 = html1 + '<input type=hidden name=nome_interrogatorio value="' + form['nome_interrogatorio'].value.replace('"', '&quot;') + '">'
				if 'occ' in form: html1 += '<input type=hidden name=occ value="' + form['occ'].value + '">'
			
			with open("./cgi-bin/tree.conllu", "w") as f:
				f.write(sentence2)
			try:
				tree = "\n".join(draw_tree("tree.conllu").splitlines()[1:])
			except Exception as e:
				tree = str(e)
			if os.path.isfile("./cgi-bin/tree.conllu"):
				os.remove("./cgi-bin/tree.conllu")

			html1 += '<div class="treeDiv" style="display:none"><b class="translateHtml">Árvore de dependências</b><pre style="overflow: auto; max-height: 90vh;">{}</pre></div>'.format(tree)
			html1 += '<br><b class="translateHtml">Edite os valores desejados:</b></div><div class="div01" style="max-width:100%; overflow-x:auto;"><table id="t01">'

			dicionario = dict()
			for a, linha in enumerate(sentence2.splitlines()):
				if '\t' in linha:
					dicionario[linha.split('\t')[0]] = linha

			for a, linha in enumerate(sentence2.splitlines()):
				if not '\t' in linha:
					html1 += f'''<tr><input class="field" value="{web.escape(linha)}" type="hidden" name="''' +str(a)+ '''-''' + '''meta"><td style="cursor:pointer; color:black; max-width: 90vw; word-wrap: break-word;" id="''' +str(a)+ '''-''' + '''meta" contenteditable=True class="annotationValue plaintext" colspan="42">''' + web.escape(linha) + '</td></tr>'
				else:
					isBold = "background-color: lightgray;" if 'tokenId' in form and linha.split('\t')[0] in form['tokenId'].value.split(",") else ""
					html1 += f'<tr style="{isBold}">'
					for b, coluna in enumerate(linha.split('\t')):
						drag = 'drag ' if b in [6] else ''
						dragId = 'id ' if b == 0 else ''
						notPipe = "" if b in [1, 2, 4, 5, 9] and coluna != "_" else "notPipe "
						tokenId = f"id_{coluna} " if b == 0 else ""
						html1 += f'''<input class="field" value="{web.escape(coluna)}" type=hidden name="''' +str(a)+ '''-''' + str(b) + f'''"><td style="cursor:pointer; color:black;" id="''' +str(a)+ '''-''' + str(b) + f'''" class="{tokenId}{drag}{dragId}{notPipe}annotationValue plaintext" contenteditable=True>''' + web.escape(coluna) + '</td>'
					html1 += '</tr>'

			html1 += '</table>'
			html1 += '</div><input type="hidden" name="textheader" value="' + form['textheader'].value + '"></label><br><br>'
			html1 += '<input type=hidden name=tokenId value="' + form['tokenId'].value + '">' if 'tokenId' in form else ''
			html1 += '</div></form>'
			achou = True
			break
	if not achou: html1 += '<span class="translateHtml">Sentença não encontrada.</span>'

	html = html1 + '''<script>function insertTextAtCursor(text) {
  var sel, range, html;
  if (window.getSelection) {
    sel = window.getSelection();
    if (sel.getRangeAt && sel.rangeCount) {
      range = sel.getRangeAt(0);
      range.deleteContents();
      range.insertNode(document.createTextNode(text));
    }
  } else if (document.selection && document.selection.createRange) {
    document.selection.createRange().text = text;
  }
}


document.querySelector(".plaintext[contenteditable]").addEventListener("paste", function(e) {
  e.preventDefault();
  if (e.clipboardData && e.clipboardData.getData) {
    var text = e.clipboardData.getData("text/plain");
    document.execCommand("insertHTML", false, text);
  } else if (window.clipboardData && window.clipboardData.getData) {
    var text = window.clipboardData.getData("Text");
    insertTextAtCursor(text);
  }
});</script>
''' + html2
	print(html)

elif os.environ['REQUEST_METHOD'] == 'POST' and form['action'].value == 'alterar':
	ud = form['conllu'].value
	if 'nome_interrogatorio' in form: nome = form['nome_interrogatorio'].value
	else: nome = ''
	if 'link_interrogatorio' in form: link = form['link_interrogatorio'].value
	else: link = ''
	if 'sentid' in form: sentid = form['sentid'].value
	else: sentid = ''
	if 'occ' in form: ocorrencias = form['occ'].value
	else: ocorrencias = ''
	text = form['textheader'].value
	tag = web.unescape(form['tag'].value) if 'tag' in form else 'NONE'
	if tag[0] == '#': tag = tag[1:]
	conlluzao = estrutura_dados.LerUD('./interrogar-ud/conllu/' + ud)
	inqueritos_concluidos = list()

	sentnum = int(form['sentnum'].value)
	if 'sentid' in form:
		if sentid != [x for x in conlluzao[sentnum] if isinstance(x, str) and x.startswith("# sent_id = ")][0].split("# sent_id = ")[1].split("\n")[0]:
			for i, sentence in enumerate(conlluzao):
				if [x for x in sentence if isinstance(x, str) and x.startswith("# sent_id = ")][0].split("# sent_id = ")[1].split("\n")[0] == sentid:
					sys.stderr.write("\n=== sentnum changed from {} to {}".format(sentnum, i))
					sentnum = i
					break
		else:
			sys.stderr.write("\b=== sentnum did not change")

	new_inquiries = []
	date = datetime.now().timestamp()
	_id = str(uuid.uuid4())
	for key in dict(form).keys():
		value = dict(form)[key]
		if re.search(r'^\d+-(\d+|meta)$', key) and not '# sent_id = ' in value.value:
			token = int(key.split('-')[0])
			if key.split('-')[1] != 'meta': coluna = int(key.split('-')[1])
			else: coluna = 'meta'
			value = web.unescape(value.value.replace("\n", "").replace("\r", ""))

			if coluna != 'meta':
				antes = '\t'.join(conlluzao[sentnum][token])
				conlluzao[sentnum][token][coluna] = value
				depois = '\t'.join(conlluzao[sentnum][token])
			else:
				antes = conlluzao[sentnum][token]
				conlluzao[sentnum][token] = value
				depois = conlluzao[sentnum][token]

			new_inquiries.append({
				'_id': _id,
				'date': date,
				'tag': tag if 'tag' in form else None,
				'conllu': ud.split(".conllu")[0],
				'textheader': form['textheader'].value, 
				'sent_id': form['sentid'].value if 'sentid' in form else None,
				'text': " ".join([x[1] if x[0] != depois.split("\t")[0] else "<b>%s</b>" % x[1] for x in conlluzao[sentnum] if not '-' in x[0] and isinstance(x, list)]) if coluna != "meta" else None,
				'before': antes, 
				'after': depois,
				'col': idx_to_col[coluna] if coluna != "meta" else depois.split(" = ")[0].split("# ")[1],
				'head': get_head(conlluzao[sentnum], conlluzao[sentnum][token]), 
				'interrogatorio': form['nome_interrogatorio'].value if 'nome_interrogatorio' in form else None,
				'occurrences': form['occ'].value if 'nome_interrogatorio' in form else None,
				'href': form['link_interrogatorio'].value if 'nome_interrogatorio' in form else None,
				})

	df = pd.DataFrame(new_inquiries)
	df.to_csv("./interrogar-ud/inqueritos/%s.csv" % _id)
			
	estrutura_dados.EscreverUD(conlluzao, './interrogar-ud/conllu/' + ud + '_inquerito')
	os.remove('./interrogar-ud/conllu/' + ud)
	os.rename('./interrogar-ud/conllu/' + ud + "_inquerito", './interrogar-ud/conllu/' + ud)

	html = '''<html><head><meta http-equiv="content-type" content="text/html; charset=UTF-8; width=device-width, initial-scale=1.0" name="viewport"></head><body><form action="../cgi-bin/inquerito.py?conllu=''' + ud + '''" method="POST" id="reenviar"><input type=hidden name=sentid value="''' + sentid + '''"><input type=hidden name=occ value="''' + ocorrencias + '''"><input type="hidden" name="textheader" value="''' + text.replace('/BOLD','').replace('@BOLD','').replace('@YELLOW/', '').replace('@PURPLE/', '').replace('@BLUE/', '').replace('@RED/', '').replace('@CYAN/', '').replace('/FONT', '') + '''"><input type=hidden name="nome_interrogatorio" value="''' + nome.replace('"', '&quot;') + '''"><input type=hidden name="link_interrogatorio" value="''' + link + '''"><input type=hidden name=finalizado value=sim>'''
	if 'tag' in form: html += '<input type=hidden name=tag value="' + form['tag'].value + '">'
	html += '<input type=hidden name=tokenId value="' + form['tokenId'].value + '">' if 'tokenId' in form else ''
	html += '''</form><script>document.cookie = "tag=''' + tag.replace('"', '\\"').replace(";", "_") + '''"; document.getElementById('reenviar').submit();</script></body></html>'''
	print(html)

exit()