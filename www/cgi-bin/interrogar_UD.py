# -*- coding: UTF-8 -*-
import re
import copy
import sys
import time
import cgi
import html as web
from collections import defaultdict

tabelaf = {      'yellow': 'green',
                        'purple': 'purple',
                        'blue': 'blue',
                        'red': 'red',
                        'cyan': 'cyan',
}

def slugify(value):
        return "".join(x if x.isalnum() or x == '.' or x == '-' else "_" for x in value)

def cleanEstruturaUD(s):
    return re.sub(r"<.*?>", "", re.sub(r"@.*?/", "", s))

def fromInterrogarToHtml(s):
    return s.replace('/BOLD', '</b>').replace('@BOLD', '<b>').replace('@YELLOW/', '<font color=' + tabelaf['yellow'] + '>').replace('@PURPLE/', '<font color=' + tabelaf['purple'] + '>').replace('@BLUE/', '<font color=' + tabelaf['blue'] + '>').replace('@RED/', '<font color=' + tabelaf['red'] + '>').replace('@CYAN/', '<font color=' + tabelaf['cyan'] + '>').replace('/FONT', '</font>')

different_distribution = ["dependentes", "children"]
coluna_tab = {
	'id': 0,
	'word': 1,
	'lemma': 2,
	'upos': 3,
	'xpos': 4,
	'feats': 5,
	'dephead': 6,
	'deprel': 7,
	'deps': 8,
	'misc': 9
}

def getDistribution(arquivoUD, parametros, coluna="lemma", filtros=[], sent_id="", criterio=0):
	import estrutura_ud

	if not criterio:
		if re.search(r"^\d+\s", parametros):
			criterio = int(parametros.split(" ", 1)[0])
			parametros = parametros.split(" ", 1)[1]
		elif len(parametros.split('"')) > 2:
			criterio = 5
		else:
			criterio = 1

	if not isinstance(arquivoUD, dict):
		sentences = main(arquivoUD, criterio, parametros, sent_id=sent_id, fastSearch=True)['output']
	else:
		sentences = arquivoUD['output']
		
	corpus = list()
	for sentence in sentences:
		if sentence:
			if coluna in different_distribution:
				sent = estrutura_ud.Sentence()
				sent.build(sentence['resultado'].replace(f"@YELLOW/", "").replace(f"@RED/", "").replace(f"@CYAN/", "").replace(f"@BLUE/", "").replace(f"@PURPLE/", "").replace("/FONT", ""))
				sent_id = sent.sent_id
			else:
				sent = sentence['resultado']
				sent_id = re.findall(r"# sent_id = (.*?)\n", re.sub(r'<.*?>', '', sent))[0]
			if sent_id not in filtros:
				corpus.append(sent)
	
	dist = list()
	all_children = {}
	lista = {}
	dispersion_files = {}
	for sentence in corpus:
		sent_id = ""
		if not coluna in different_distribution:	
			for t, token in enumerate(sentence.splitlines()):
				if not sent_id:
					if token.startswith("# sent_id = "):
						sent_id = token.split("# sent_id = ")[1]
				elif ('<b>' in token or '</b>' in token) and len(token.split("\t")) > 5:
					entrada = re.sub(r'@.*?/', '', re.sub(r'<.*?>', '', token.split("\t")[coluna_tab[coluna]].replace("/FONT", "")))
					dist.append(entrada)
					if not entrada in lista:
						lista[entrada] = 0
					lista[entrada] += 1
					if '-' in sent_id:
						if not entrada in dispersion_files:
							dispersion_files[entrada] = []
						filename = sent_id.rsplit("-", 1)[0]
						if not filename in dispersion_files[entrada]:
							dispersion_files[entrada].append(filename)
		if coluna in different_distribution:
			for t, token in enumerate(sentence.tokens):
				if '<b>' in token.to_str() or "</b>" in token.to_str():
					if not coluna in different_distribution:
						dist.append(re.sub(r'<.*?>', '', token.__dict__[coluna]))
					elif coluna in ["dependentes", "children"]:
						children = [t]
						children_already_seen = []
						children_future = []
						while children_already_seen != children:
							for child in children:
								if not child in children_already_seen:
									children_already_seen.append(child)
								for _t, _token in enumerate(sentence.tokens):
									if cleanEstruturaUD(_token.dephead) == cleanEstruturaUD(sentence.tokens[child].id):
										children_future.append(_t)
							[children.append(x) for x in children_future if x not in children]
							children_future = []
						children_list = [cleanEstruturaUD(sentence.tokens[x].word) if x != t else "<b>" + cleanEstruturaUD(sentence.tokens[x].word) + "</b>" for x in sorted(children)]
						if len(children_list) > 1:
							entrada = " ".join(children_list)
							dist.append(entrada)
							if not entrada in lista:
								lista[entrada] = 0
							lista[entrada] += 1
							if '-' in sentence.sent_id:
								filename = sentence.sent_id.rsplit("-", 1)[0]
								if not entrada in dispersion_files:
									dispersion_files[entrada] = []
								if not filename in dispersion_files[entrada]:
									dispersion_files[entrada].append(filename)
							if children_list:
								if not entrada in all_children:
									all_children[entrada] = []
								all_children[entrada].append(sentence.sent_id)


	#dicionario = dict()
	#for entrada in dist:
		#entrada = entrada.replace("<b>", "").replace("</b>", "")
		#if not entrada in dicionario: dicionario[entrada] = 1
		#else: dicionario[entrada] += 1

	#lista = list()
	#for entrada in dicionario:
		#lista.append((entrada, dicionario[entrada]))

	#freq = dict()
	#for entrada in dicionario:
		#if not dicionario[entrada] in freq: freq[dicionario[entrada]] = 1
		#else: freq[dicionario[entrada]] += 1
	#lista_freq = list()
	#for entrada in freq:
		#lista_freq.append((entrada, freq[entrada]))

	return {"all_children": all_children, "lista": lista, "dist": len(dist), "dispersion_files": dispersion_files}

#Crio a função que vai ser chamada seja pelo HTML ou seja pelo terminal
def main(arquivoUD, criterio, parametros, limit=0, sent_id="", fastSearch=False, separate=False):
	parametros = parametros.strip()
	pesquisa = ""

	if criterio in [1]:
		import estrutura_ud
		if isinstance(arquivoUD, str):
			with open(arquivoUD) as f:
				arquivoUD = f.read()
		else:
			arquivoUD = arquivoUD.to_str()
				
	
	#Lê o arquivo UD
	if criterio in [3, 4]:
		import estrutura_dados
		import estrutura_ud
		qualquercoisa = estrutura_dados.LerUD(arquivoUD)

	if criterio in [2]:
		import estrutura_ud
		if isinstance(arquivoUD, str):
			if "head_token" in parametros or "next_token" in parametros or "previous_token" in parametros:
				corpus = estrutura_ud.Corpus(recursivo=True, sent_id=sent_id)
			else:
				corpus = estrutura_ud.Corpus(recursivo=False, sent_id=sent_id)
			start = time.time()
			corpus.load(arquivoUD)
			sys.stderr.write("\ncorpus.build: " + str(time.time() - start))
		else:
			corpus = arquivoUD
			

	#Cria a lista que vai ser enviada seja ao terminal ou ao HTML
	output = list()
	casos = 0

	#Regex
	tabela = ['@YELLOW/','@PURPLE/','@BLUE/','@RED/','@CYAN/']
	
	if criterio == 1:
		start = time.time()
		sentence = ""
		f = arquivoUD.splitlines(keepends=True)
		for line in f:
			if line.strip():
				sentence += line
			else:
				if limit and len(output) == limit:
					break
				regex = re.findall('(' + parametros + ')', sentence, flags=re.I)
				if regex:
					casos += len(regex)
					new_sentence = re.sub('(' + parametros + ')', r'<b>\1</b>', sentence, flags=re.I)
					tokens = list()
					header = '!@#' if not '# text = ' in new_sentence else '# text = ' + new_sentence.split("# text = ")[1].split("\n")[0]
					for linha in new_sentence.splitlines():
						if 'b>' in linha and '\t' in linha:
							if '\\' in linha:
								linha = re.sub(r"\\(\d+)", r"\\\\\1", linha, flags=re.I)
							tokens.append(linha.split('\t')[1].replace('<b>','').replace('</b>',''))
					header2 = header
					for token in tokens:
						header2 = re.sub(r'\b' + re.escape(token) + r'\b', '<b>' + token + '</b>', header2, flags=re.I)
					for reg in regex:
						if not isinstance(reg, str):
							for i, grupo in enumerate(reg):
								if i != 0:
									if grupo and i-1 < len(tabela):
										token = ""
										if '\t' in grupo:
											token = grupo.split('\t')[1]
										if token:
											header2 = re.sub(r'\b' + re.escape(token) + r'\b', tabela[i-1] + token + '/FONT', header2, flags=re.I)
					new_sentence = new_sentence.replace(header, header2)
					output.append(new_sentence)
				sentence = ""
		sys.stderr.write(f"\ncriterio 1: {time.time() - start}")

	#If critério 2
	if criterio == 2:

		#Variáveis
		y = parametros.split('#')[0].strip()
		z = int(parametros.split('#')[1].strip())
		k = parametros.split('#')[2].strip()
		w = int(parametros.split('#')[3].strip())
		for sentence in corpus.sentences.values():
			for token in sentence.tokens:
				colunas = token.to_str().split("\t")
				if any(colunas[z-1] == x for x in y.split("|")):
					descarta = False
					for _token in sentence.tokens:
						_colunas = _token.to_str().split("\t")
						if any(_colunas[w-1] == x for x in k.split("|")) and _token.dephead == token.id:
							descarta = True
					if not descarta:
						output.append(re.sub(r"\b" + re.escape(token.word) + r"\b", "<b>" + re.escape(token.word) + "</b>", sentence.to_str()))
						casos += 1
					
	#Regex Independentes
	if criterio == 3:
		regras = [x.strip() for x in parametros.split('::')]

		for a, sentence in enumerate(qualquercoisa):
			sentence2 = sentence
			for b, linha in enumerate(sentence):
				linha2 = linha
				if isinstance(linha2, list):
					sentence2[b] = "\t".join(sentence2[b])
			sentence2 = "\n".join(sentence2)
			descarta = False
			for regranum, regra in enumerate(regras):
				if regra[0] == '!':
					regex = re.search(regra[1:], sentence2, flags=re.IGNORECASE|re.MULTILINE)
					casos += len(re.findall(regra[1:], sentence2, flags=re.I|re.M))
				else:
					regex = re.search(regra, sentence2, flags=re.IGNORECASE|re.MULTILINE)
					casos += len(re.findall(regra, sentence2, flags=re.I|re.M))
				if (regra[0] == '!' and regex) or (regra[0] != '!' and not regex):
					descarta = True
					break
				sentence2 = re.sub('(' + regra + ')', tabela[regranum] + r'<b>\1</b>/FONT', sentence2, flags=re.IGNORECASE|re.MULTILINE)
			if not descarta:
				tokens = list()
				header = '!@#'
				for linha in sentence2.splitlines():
					if '# text = ' in linha:
						header = linha
					if 'b>' in linha and '\t' in linha:
						if '@' in linha:
							tokens.append((linha.split('\t')[1].replace('<b>','').replace('</b>','').replace('@' + linha.split('@')[1].split('/')[0] + '/', ''), '@' + linha.split('@')[1].split('/')[0] + '/'))
							lastcolor = '@' + linha.split('@')[1].split('/')[0] + '/'
						else:
							tokens.append((linha.split('\t')[1].replace('<b>','').replace('</b>',''), lastcolor))
				header2 = header
				for token in tokens:
					header2 = re.sub(r'\b' + re.escape(token[0]) + r'\b', token[1] + '<b>' + token[0] + '</b>/FONT', header2)
				sentence2 = sentence2.replace(header, header2)
				output.append(sentence2.splitlines())

	#pais e filhos
	if criterio == 4:
		filho = parametros.split('::')[0].strip()
		pai = parametros.split('::')[1].strip()
		
		negativo_filho = False
		negativo_pai = False
		if filho[0] == '!':
			negativo_filho = True
			filho = ''.join(filho[1:])
		if pai[0] == '!':
			negativo_pai = True
			pai = ''.join(pai[1:])

		for a, sentenca in enumerate(qualquercoisa):
			acheifilho = 'não'
			acheipai = 'não'
			descarta = False
			for b, linha in enumerate(sentenca):
				if isinstance(linha, list):
					if re.search(filho, '\t'.join(linha), flags=re.IGNORECASE|re.MULTILINE):
						acheifilho = (linha, b)
				if isinstance(linha, list):
					if re.search(pai, '\t'.join(linha), flags=re.IGNORECASE|re.MULTILINE):
						acheipai = (linha, b)
				
				if not negativo_filho and not negativo_pai and acheipai != 'não' and acheifilho != 'não' and acheipai[0][0] == acheifilho[0][6]:
					for c, linha in enumerate(sentenca):
						if '# text' in linha:
							qualquercoisa[a][c] = re.sub(r'\b' + re.escape(acheipai[0][1]) + r'\b', '<b>@BLUE/' + acheipai[0][1] + '/FONT</b>', qualquercoisa[a][c], flags=re.IGNORECASE|re.MULTILINE)
							qualquercoisa[a][c] = re.sub(r'\b' + re.escape(acheifilho[0][1]) + r'\b', '<b>@RED/' + acheifilho[0][1] + '/FONT</b>', qualquercoisa[a][c], flags=re.IGNORECASE|re.MULTILINE)
							break
					qualquercoisa[a][acheipai[1]] = ('<b>@BLUE/' + '\t'.join(qualquercoisa[a][acheipai[1]]) + '/FONT</b>').split('\t')
					qualquercoisa[a][acheifilho[1]] = ('<b>@RED/' + '\t'.join(qualquercoisa[a][acheifilho[1]]) + '/FONT</b>').split('\t')
					output.append(qualquercoisa[a])
					break
				
				elif negativo_filho and acheipai != 'não' and acheifilho != 'não' and acheipai[0][0] == acheifilho[0][6]:
					descarta = True
					break
				
				elif negativo_pai and acheifilho != 'não' and acheipai != 'não' and acheipai[0][0] == acheifilho[0][6]:
					descarta = True
					break

			if negativo_filho and acheipai != 'não' and acheifilho != 'não' and not descarta:
				for c, linha in enumerate(sentenca):
					if '# text' in linha:
						qualquercoisa[a][c] = re.sub(r'\b' + re.escape(acheipai[0][1]) + r'\b', '<b>@BLUE/' + acheipai[0][1] + '/FONT</b>', qualquercoisa[a][c], flags=re.IGNORECASE|re.MULTILINE)
						break
				qualquercoisa[a][acheipai[1]] = ('<b>@BLUE/' + '\t'.join(qualquercoisa[a][acheipai[1]]) + '/FONT</b>').split('\t')
				output.append(qualquercoisa[a])
				
			elif negativo_pai and acheipai != 'não' and acheifilho != 'não' and not descarta:
				for c, linha in enumerate(sentenca):
					if '# text' in linha:
						qualquercoisa[a][c] = re.sub(r'\b' + re.escape(acheifilho[0][1]) + r'\b', '<b>@BLUE/' + acheifilho[0][1] + '/FONT</b>', qualquercoisa[a][c], flags=re.IGNORECASE|re.MULTILINE)
						break
				qualquercoisa[a][acheifilho[1]] = ('<b>@BLUE/' + '\t'.join(qualquercoisa[a][acheifilho[1]]) + '/FONT</b>').split('\t')
				output.append(qualquercoisa[a])
					
			elif negativo_filho and acheipai != 'não' and acheifilho == 'não':
				for c, linha in enumerate(sentenca):
					if '# text' in linha:
						qualquercoisa[a][c] = re.sub(r'\b' + re.escape(acheipai[0][1]) + r'\b', '<b>@BLUE/' + acheipai[0][1] + '/FONT</b>', qualquercoisa[a][c], flags=re.IGNORECASE|re.MULTILINE)
						break
				qualquercoisa[a][acheipai[1]] = ('<b>@BLUE/' + '\t'.join(qualquercoisa[a][acheipai[1]]) + '/FONT</b>').split('\t')
				output.append(qualquercoisa[a])
			
			elif negativo_pai and acheifilho != 'não' and acheipai == 'não':
				for c, linha in enumerate(sentenca):
					if '# text' in linha:
						qualquercoisa[a][c] = re.sub(r'\b' + re.escape(acheifilho[0][1]) + r'\b', '<b>@RED/' + acheifilho[0][1] + '/FONT</b>', qualquercoisa[a][c], flags=re.IGNORECASE|re.MULTILINE)
						break
				qualquercoisa[a][acheifilho[1]] = ('<b>@RED/' + '\t'.join(qualquercoisa[a][acheifilho[1]]) + '/FONT</b>').split('\t')
				output.append(qualquercoisa[a])

	#Python

	if criterio == 5:
		
		parametros = parametros.split(" and ")
		for t, parametro in enumerate(parametros):
			if not any(x in parametros[t] for x in [' = ', '==', '!=', ' < ', ' > ']):
				parametros[t] = re.findall(r'@?"[^"]+?"', parametros[t].replace(" ", ""))
				parametros[t] = [("@" if "@" in x else "") + ("next_token."*i) + "word = " + x.replace("@", "") for i, x in enumerate(parametros[t]) if x]
				parametros[t] = " and ".join(parametros[t])
		parametros = " and ".join(parametros)
		pesquisa = parametros

		pesquisa = pesquisa.replace(" = ", " == ")
		pesquisa = pesquisa.replace(" @", " ")
		if pesquisa[0] == "@": pesquisa = pesquisa[1:]
		pesquisa = pesquisa.replace("  ", " ").strip()
		pesquisa = pesquisa.replace(" == ", " == token.")
		pesquisa = pesquisa.replace(" === ", " === token.")
		pesquisa = pesquisa.replace(" != ", " != token.")
		pesquisa = pesquisa.replace(" !== ", " !== token.")
		pesquisa = pesquisa.replace(" > ", " > token.")
		pesquisa = pesquisa.replace(" < ", " < token.")
		pesquisa = pesquisa.replace(" >= ", " >= token.")
		pesquisa = pesquisa.replace(" <= ", " <= token.")
		pesquisa = "token." + pesquisa
		pesquisa = pesquisa.replace(" and ", " and token.")
		pesquisa = pesquisa.replace(" or ", " or token.")
		pesquisa = pesquisa.replace(" in ", " in token.")
		pesquisa = pesquisa.replace(" text ", " sentence.text ")
		pesquisa = pesquisa.replace(" sent_id ", " sentence.sent_id ")
		pesquisa = pesquisa.replace('token."', '"')
		pesquisa = pesquisa.replace('token.[', '[')
		pesquisa = pesquisa.replace('token.(', '(')
		
		pesquisa = pesquisa.replace('token.not', 'not')
		pesquisa = pesquisa.replace('token.token.', 'token.')
		pesquisa = pesquisa.replace('token.sentence.', 'sentence.')
		pesquisa = pesquisa.replace("token.text", "sentence.text")
		pesquisa = pesquisa.replace("token.sent_id", "sentence.sent_id")
		pesquisa = pesquisa.replace('token.int(', 'int(')
		#pesquisa = pesquisa.replace("token.and", "and")
#		pesquisa = pesquisa.replace("== int(", "==int(")
		pesquisa = re.sub(r'token\.([1234567890])', r'\1', pesquisa)

		indexed_conditions = {x.split(" == ")[0].strip().split("token.", 1)[1]: x.split(" == ")[1].strip().replace('"', '') for x in pesquisa.split(" and ") if ' == ' in x and 'token.' in x and not any(y in x for y in ["head_token", "previous_token", "next_token"])} #["head_token.head", "head_token.next", "head_token.previous", "next_token.head", "next_token.next", "next_token.previous", "previous_token.head", "previous_token.next", "previous_token.previous"])}
		pesquisa = re.sub(r"token\.([^. ]+?)(\s|$)", r"token.__dict__['\1']\2", pesquisa)
		
		pesquisa = re.sub(r'(\S+)\s==\s(\".*?\")', r'any( re.search( r"^" + r\2 + r"$", x ) for x in \1.split("ddd") )', pesquisa) #ddd provisório enquanto split na barra em pé não funciona
		pesquisa = re.sub(r'(\S+)\s===\s(\".*?\")', r'all( re.search( r"^" + r\2 + r"$", x ) for x in \1.split("|") )', pesquisa)
		pesquisa = re.sub(r'(\S+)\s!=\s(\".*?\")', r'not any( re.search( r"^" + r\2 + r"$", x ) for x in \1.split("ddd") )', pesquisa)
		pesquisa = re.sub(r'(\S+)\s!==\s(\".*?\")', r'not all( re.search( r"^" + r\2 + r"$", x ) for x in \1.split("|") )', pesquisa)
		pesquisa = pesquisa.strip()
		with open("pesquisa", "w") as f:
			f.write(pesquisa)

		if (".__dict__['id']" in pesquisa or ".__dict__['dephead']" in pesquisa) and (not "int(" in pesquisa) and (" < " in pesquisa or " > " in pesquisa):
			pesquisa = re.sub(r"(\S+\.__dict__\['(id|dephead)'\])", r"int(\1)", pesquisa)

		identificador = "token"

		if parametros[0] == "@":
			parametros = parametros[1:]
		
		arroba = parametros.split(" ")[0] if not ' @' in parametros else parametros.rsplit(" @", 1)[1].replace("int(", "").split(")")[0].split(" ")[0].replace("(", "")
		arroba = "token." + arroba
		arroba = arroba.replace("token.token", "token")
		arroba = arroba.rsplit(".", 1)[0]

		agilizar = re.findall(r'"([^"]*)"', parametros)

		import estrutura_ud
		if isinstance(arquivoUD, str):
			if "head_token" in parametros or "next_token" in parametros or "previous_token" in parametros:
				corpus = estrutura_ud.Corpus(recursivo=True, sent_id=sent_id, keywords=agilizar)
			else:
				corpus = estrutura_ud.Corpus(recursivo=False, sent_id=sent_id, keywords=agilizar)
			start = time.time()
			corpus.load(arquivoUD)
			sys.stderr.write("\ncorpus.build: " + str(time.time() - start))
		else:
			corpus = arquivoUD

		start = time.time()
		casos = []
	
		t1 = time.time()
		if indexed_conditions:
			sentences = defaultdict(list)
			tokens = defaultdict(list)
			values = {}
			for sent_id in corpus.sentences:
				for col in indexed_conditions:
					if col in corpus.sentences[sent_id].processed:
						values = re.findall(r"\n(" + indexed_conditions[col] + r")\n", "\n" + "\n\n".join(list(corpus.sentences[sent_id].processed[col])) + "\n")
						for value in values:
							if value:
								if not isinstance(value, str):
									value = value[0]
								tokens[col].extend(corpus.sentences[sent_id].processed[col][value])
			for col in tokens:
				tokens[col] = set(tokens[col])
			tokens_filtered = []
			if tokens.values():
				tokens_filtered = set.intersection(*list(tokens.values()))
			'''
			priority = ['lemma', 'word', 'deprel', 'upos']
			priority_possible = []
			for col in indexed_conditions:
				if col in priority:
					priority_possible.append(priority.index(col))
			if priority_possible:
				col = priority[min(priority_possible)]
			else:
				col = list(indexed_conditions)[0]
			cols = list(indexed_conditions)
			cols.remove(col)
			'''
			for token in tokens_filtered:
				sent_id = token.split("<tok>")[0]
				t = int(token.split("<tok>")[1])
				sentences[sent_id].append(t)
		else:
			sentences = corpus.sentences
		sys.stderr.write(f"\nindexing: {time.time() - t1}")

		t1 = time.time()
		for sent_id in sentences:
			sentence = corpus.sentences[sent_id]
			sentence2 = sentence
			clean_text = [x.word for x in sentence2.tokens if not '-' in x.id and not '.' in x.id]
			clean_id = [x.id for x in sentence2.tokens if not '-' in x.id and not '.' in x.id]
			corresponde = 0
			tokens = sentence2.tokens_to_str()
			map_id = {x: t for t, x in enumerate(clean_id)}
			if limit and limit == len(output):
				break
			condition = "global sim; sim = 0"
			
			condition += '''
if not indexed_conditions:
	available_tokens = list(range(len(sentence.tokens)))
else:
	available_tokens = sentences[sent_id]
for token_t in available_tokens:
	token = sentence.tokens[token_t]
	try:
		if (not "-" in token.id and not '.' in token.id and (''' + pesquisa + ''')) :
			corresponde = 1
			clean_text[map_id[token.id]] = "@BLUE/" + clean_text[map_id[token.id]] + "/FONT"
			tokens = tokens.replace(token.string, "@BLUE/" + token.string + "/FONT")
	'''#try por causa de não ter um next_token no fim de sentença, por ex.
			if "token.head_token" in pesquisa:
				condition += '''
			clean_text[map_id[token.head_token.id]] = "@RED/" + clean_text[map_id[token.head_token.id]] + "/FONT"
			tokens = tokens.replace(token.head_token.string, "@RED/" + token.head_token.string + "/FONT")'''
			if "token.next_token" in pesquisa:
				condition += '''
			clean_text[map_id[token.next_token.id]] = "@BLUE/" + clean_text[map_id[token.next_token.id]] + "/FONT"
			tokens = tokens.replace(token.next_token.string, "@BLUE/" + token.next_token.string + "/FONT")'''
			if "token.previous_token" in pesquisa:
				condition += '''
			clean_text[map_id[token.previous_token.id]] = "@BLUE/" + clean_text[map_id[token.previous_token.id]] + "/FONT"
			tokens = tokens.replace(token.previous_token.string, "@BLUE/" + token.previous_token.string + "/FONT")'''
			condition += '''
			clean_text[map_id['''+arroba+'''.id]] = "<b>" + clean_text[map_id['''+arroba+'''.id]] + "</b>"'''		
			
			exec(condition + '''
			casos.append(1)
			arroba_id = '''+arroba+'''.id
			tokens = tokens.splitlines()
			for l, linha in enumerate(tokens):
				if linha.split("\\t")[0] == arroba_id or ("/" in linha.split("\\t")[0] and linha.split("\\t")[0].split("/")[1] == arroba_id):
					tokens[l] = "<b>" + tokens[l] + "</b>"
			tokens = "\\n".join(tokens)

			if separate:
				corresponde = 0
				final = "# clean_text = " + " ".join(clean_text) + "\\n" + sentence2.metadados_to_str() + "\\n" + tokens
				output.append(final)
			
	except Exception as e:
		print(str(e))
		print(token.to_str())
		pass
if corresponde and not separate:
	corresponde = 0
	final = "# clean_text = " + " ".join(clean_text) + "\\n" + sentence2.metadados_to_str() + "\\n" + tokens
	output.append(final)''')
		sys.stderr.write("\ncritério 5: " + str(time.time() - start))
		casos = len(casos)
		sys.stderr.write(f"\nfor each sentence: {time.time() - t1}")
	#Transforma o output em lista de sentenças (sem splitlines e sem split no \t)
	if criterio not in [5, 2, 1]:
		for a, sentence in enumerate(output):
			for b, linha in enumerate(sentence):
				if isinstance(linha, list):
					sentence[b] = "\t".join(sentence[b])
			output[a] = "\n".join(sentence)

	start = time.time()
	for i, final in enumerate(output):
		if not fastSearch:
			anotado = estrutura_ud.Sentence(recursivo=False)
			estruturado = estrutura_ud.Sentence(recursivo=False)
			anotado.build(web.escape(final.replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<font color=' + tabelaf['yellow'] + '>', '@YELLOW/').replace('<font color=' + tabelaf['red'] + '>', '@RED/').replace('<font color=' + tabelaf['cyan'] + '>', '@CYAN/').replace('<font color=' + tabelaf['blue'] + '>', '@BLUE/').replace('<font color=' + tabelaf['purple'] + '>', '@PURPLE/').replace('</font>', '/FONT')))		
			estruturado.build(web.unescape(final).replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<font color=' + tabelaf['yellow'] + '>', '@YELLOW/').replace('<font color=' + tabelaf['red'] + '>', '@RED/').replace('<font color=' + tabelaf['cyan'] + '">', '@CYAN/').replace('<font color=' + tabelaf['blue'] + '>', '@BLUE/').replace('<font color=' + tabelaf['purple'] + '>', '@PURPLE/').replace('</font>', '/FONT').replace('@BOLD', '').replace('/BOLD', '').replace('@YELLOW/', '').replace('@RED/', '').replace('@CYAN/', '').replace('@BLUE/', '').replace('@PURPLE/', '').replace('/FONT', ''))			
		else:
			anotado = ""
			estruturado = ""
		output[i] = {
			'resultado': final,
			'resultadoAnotado': anotado,
			'resultadoEstruturado': estruturado,
		}
	#sys.stderr.write("\nbuscaDicionarios: " + str(time.time() - start))
	
	sentences = {}
	if not fastSearch:
		sentences = {x['resultadoEstruturado'].sent_id: i for i, x in enumerate(output)}

	return {'output': output, 'casos': casos, 'sentences': sentences, 'parameters': pesquisa if pesquisa else parametros}

#Ele só pede os inputs se o script for executado pelo terminal. Caso contrário (no caso do código ser chamado por uma página html), ele não pede os inputs, pois já vou dar a ele os parâmetros por meio da página web
if __name__ == '__main__':
	import sys
	if len(sys.argv) < 2:
		arquivoUD = input('arraste arquivo:\n').replace("'","").replace('"','').strip()
	else:
		arquivoUD = sys.argv[1]
	
	criterio=int(input('qual criterio de procura? '))
	while criterio > 5:
	    print('em desenvolvimento')
	    criterio=int(input('qual criterio de procura? '))

	if criterio == 1 or criterio == 3:
		parametros = input('Expressão regular:\n')

	if criterio == 2:
		y=input('Se um token X marcado como: ')
		z=int(input('Na coluna: '))
		k=input('e nenhum outro token com valor: ')
		w=int(input('na coluna: '))
		nome=input('nomeie sua criação:\n')
		parametros  = y + '#' + str(z) + '#' + k + '#' + str(w)
		
	if criterio == 4:
		filho = input('Filho: ')
		pai = input('Pai: ')
		parametros = filho + ' :: ' + pai

	if criterio == 5:
		parametros = input("Expressão de busca:\n")

	#Chama a função principal e printo o resultado, dando a ela os parâmetros dos inputs
	printar = main(arquivoUD, criterio, parametros)['output']
	
	if criterio in [1, 2, 3, 4]:
		for a, sentence in enumerate(printar):
			printar[a] = printar[a].splitlines()
			for i, linha in enumerate(printar[a]):
				if isinstance(linha, list):
					printar[a][i] = '\t'.join(printar[a][i])
			printar[a] = '\n'.join(printar[a])
		printar = '\n\n'.join(printar)
	elif criterio in [5]:
		printar = "\n\n".join([x['resultado'] for x in printar])
		print(getDistribution(arquivoUD, criterio, parametros))
	
	print(printar)
	
