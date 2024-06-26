# -*- coding: UTF-8 -*-
import re
import sys
import time
import os
import html as web
import multiprocessing
from collections import defaultdict
from utils import query_is_python, query_is_tokens, cleanEstruturaUD
from estrutura_ud import col_to_idx

tabelaf = {
	'yellow': 'green',
	'purple': 'purple',
	'blue': 'blue',
	'red': 'red',
	'cyan': 'cyan',
}


def shortcuts(s):
	return s.replace(".pt", ".previous_token").replace(".ht", ".head_token").replace(".nt", ".next_token")

def slugify(value):
	return "".join(x if x.isalnum() or x == '.' or x == '-' else "_" for x in value)

different_distribution = ["dependentes", "children"]

def getDistribution(arquivoUD, parametros, coluna="lemma", filtros=[], sent_id="", criterio=0):
	import estrutura_ud
	parametros = parametros.strip().replace('“', '"').replace('”', '"')

	if not criterio:
		if re.search(r"^\d+\s", parametros):
			criterio = int(parametros.split(" ", 1)[0])
			parametros = parametros.split(" ", 1)[1]
		elif query_is_python(parametros) or query_is_tokens(parametros):
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
			sent = sentence['resultado']
			if sent_id not in filtros:
				corpus.append(sent)
	
	dist = list()
	all_children = {}
	lista = {}
	dispersion_files = {}
	for sentence in corpus:
		sent_id = cleanEstruturaUD(sentence).split("# sent_id = ")[1].split("\n")[0]
		if not coluna in different_distribution:
			for t, token in enumerate(sentence.splitlines()):
				if ('<b>' in token or '</b>' in token) and '\t' in token:
					if coluna in col_to_idx:
						idx = col_to_idx[coluna]
					else:
						idx = int(coluna.split("col")[1])-1
					entrada = cleanEstruturaUD(token.split("\t")[idx])
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
		elif coluna in different_distribution:
			frase = estrutura_ud.Sentence()
			frase.build(cleanEstruturaUD(sentence))
			bold_tokens = [cleanEstruturaUD(x).split("\t")[0] for x in sentence.splitlines() if '\t' in x and '<b>' in x]
			sentence = frase
			for t, token in enumerate(sentence.tokens):
				if token.id in bold_tokens:
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
def main(arquivoUD, criterio, parametros, limit=0, sent_id="", fastSearch=False):
	parametros = parametros.strip().replace('“', '"').replace('”', '"')
	pesquisa = ""

	if not criterio:
		if query_is_python(parametros) or query_is_tokens(parametros):
			criterio = 5
		else:
			criterio = 1

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
						output.append(re.sub(r"\b" + re.escape(token.word) + r"\b", "<b>" + token.word + "</b>", sentence.to_str()))
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
		indexed_conditions = None
		agilizar = None
		any_of_keywords = None
		if query_is_tokens(parametros):
			parametros = parametros.replace(" ", "")
			arroba = "token"
		else:
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
			#pesquisa = pesquisa.replace(" sent_id ", " sentence.sent_id ")
			pesquisa = pesquisa.replace("sentence.sent_id ", "sent_id ")
			pesquisa = pesquisa.replace('token."', '"')
			pesquisa = pesquisa.replace('token.[', '[')
			pesquisa = pesquisa.replace('token.(', '(')
			
			pesquisa = pesquisa.replace('token.not', 'not')
			pesquisa = pesquisa.replace('token.token.', 'token.')
			pesquisa = pesquisa.replace('token.sentence.', 'sentence.')
			pesquisa = pesquisa.replace("token.text", "sentence.text")
			pesquisa = pesquisa.replace("token.sent_id", "sent_id")
			pesquisa = pesquisa.replace('token.int(', 'int(')
			#pesquisa = pesquisa.replace("token.and", "and")
			#pesquisa = pesquisa.replace("== int(", "==int(")
			pesquisa = re.sub(r'token\.([1234567890])', r'\1', pesquisa)

			pesquisa = shortcuts(pesquisa)

			indexed_conditions = {
				x.split(" == ")[0].strip().split("token.", 1)[1]: x.split(" == ")[1].strip().replace('"', '') for x in pesquisa.split(" and ") if ' == ' in x and 
				'token.' in x and 
				not any(y in x for y in ["head_token", "previous_token", "next_token"])
				}
			pesquisa = re.sub(r"token\.([^. ]+?)(\s|$)", r"token.__dict__['\1']\2", pesquisa)
			
			pesquisa = re.sub(r'(\S+)\s==\s(\".*?\")', r're.search( r"^(" + r\2 + r")$", \1 )', pesquisa)
			pesquisa = re.sub(r'(\S+)\s===\s(\".*?\")', r'all( re.search( r"^(" + r\2 + r")$", x ) for x in \1.split("|") )', pesquisa)
			pesquisa = re.sub(r'(\S+)\s!=\s(\".*?\")', r'not re.search( r"^(" + r\2 + r")$", \1 )', pesquisa)
			pesquisa = re.sub(r'(\S+)\s!==\s(\".*?\")', r'not all( re.search( r"^(" + r\2 + r")$", x ) for x in \1.split("|") )', pesquisa)
			pesquisa = pesquisa.strip()
			sys.stderr.write("\nquery: " + pesquisa + "\n")
			if "upos != \"(" in parametros:
				sys.stderr.write("\n{}\n".format(pesquisa))

			if (".__dict__['id']" in pesquisa or ".__dict__['dephead']" in pesquisa) and (not "int(" in pesquisa) and (" < " in pesquisa or " > " in pesquisa):
				pesquisa = re.sub(r"(\S+\.__dict__\['(id|dephead)'\])", r"int(\1)", pesquisa)

			identificador = "token"

			if parametros[0] == "@":
				parametros = parametros[1:]
			
			arroba = parametros.split(" ")[0] if not ' @' in parametros else parametros.rsplit(" @", 1)[1].replace("int(", "").split(")")[0].split(" ")[0].replace("(", "")
			arroba = "token." + arroba
			arroba = arroba.replace("token.token", "token")
			arroba = arroba.rsplit(".", 1)[0]
			arroba = shortcuts(arroba)

			agilizar = re.findall(r'"([^"]*)"', parametros)

		import estrutura_ud
		if isinstance(arquivoUD, str):
			if any(x in pesquisa for x in ["head_token", "next_token", "previous_token"]):
				corpus = estrutura_ud.Corpus(recursivo=True, keywords=agilizar if not '!=' in parametros and agilizar else "", any_of_keywords=any_of_keywords if any_of_keywords else "")
			else:
				corpus = estrutura_ud.Corpus(recursivo=False, keywords=agilizar if not '!=' in parametros and agilizar else "", any_of_keywords=any_of_keywords if any_of_keywords else "")
			start = time.time()
			corpus.load(arquivoUD)
		else:
			corpus = arquivoUD

		start = time.time()
		casos = []
	
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
			for token in tokens_filtered:
				sent_id = token.split("<tok>")[0]
				t = int(token.split("<tok>")[1])
				sentences[sent_id].append(t)
		else:
			sentences = corpus.sentences
		sys.stderr.write(f"\nindexing: {time.time() - start}")

		start = time.time()
		if not query_is_tokens(parametros):
			n_process = multiprocessing.cpu_count()
			args = []
			for sent_id in sentences.keys():
				sentence = corpus.sentences[sent_id]
				clean_id = [x.id for x in sentence.tokens if not '-' in x.id and not '.' in x.id]
				args.append({
					'available_tokens': list(range(len(sentence.tokens))) if not indexed_conditions else sentences[sent_id],
					'text_tokens': [x.word for x in sentence.tokens if not '-' in x.id and not '.' in x.id],
					'tokens': sentence.tokens_to_str(),
					'sentence_tokens': sentence.tokens,
					'sentence_metadados': sentence.metadados_to_str(),
					'map_id': {x: t for t, x in enumerate(clean_id)},
					'sent_id': sent_id,
					})
			args = chunks(args, n_process)
			if not 'win' in sys.platform:
				# Multiprocessing está bugando no Windows
				with multiprocessing.Pool(n_process) as p:
					for result in p.starmap(process_sentences, [(arg, pesquisa, arroba, limit) for arg in args if arg]):
						output.extend(result[0])
						casos.extend(result[1])
			else:
				for arg in args:
					if arg:
						result = process_sentences(arg, pesquisa, arroba, limit)
						output.extend(result[0])
						casos.extend(result[1])
		else:
			if parametros != "tokens=":
				query = parametros.split("tokens=")[1]
				sent_ids = query.split("|")
				for part in sent_ids:
					sent_id = part.split(":")[0]
					token_ids = part.split(":")[1].split(",")
					sentence = corpus.sentences[sent_id]
					text_tokens = [x.word for x in sentence.tokens if not '-' in x.id and not '.' in x.id]
					clean_id = [x.id for x in sentence.tokens if not '-' in x.id and not '.' in x.id]
					map_id = {x: t for t, x in enumerate(clean_id)}
					tokens = sentence.tokens_to_str()
					for token_id in token_ids:
						token = sentence.tokens[sentence.map_token_id[token_id]]
						casos.append(token)
						if token.id in map_id:
							text_tokens[map_id[token.id]] = "<b>" + text_tokens[map_id[token.id]] + "</b>"
						token_new_string = "<b>" + token.string + "</b>"
						tokens = tokens.replace(token.string, token_new_string)
						token.string = token_new_string
					final = "# text_tokens = " + " ".join(text_tokens) + "\n" + sentence.metadados_to_str() + "\n" + tokens
					output.append(final)
		casos = len(casos)
		sys.stderr.write(f"\nfor each sentence: {time.time() - start}")
	
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
	
	sentences = {x['resultado'].split("# sent_id = ")[1].split("\n")[0]: i for i, x in enumerate(output)}

	return {'output': output, 'casos': casos, 'sentences': sentences, 'parameters': pesquisa if pesquisa else parametros}

def process_sentences(args, pesquisa, arroba, limit):
	output = []
	casos = []
	sys.stderr.write("\nProcessing %s sentences, process no. %s" % (len(args), os.getpid()))
	for arg in args:
		available_tokens = arg['available_tokens']
		text_tokens = arg['text_tokens']
		tokens = arg['tokens']
		sentence_tokens = arg['sentence_tokens']
		sentence_metadados = arg['sentence_metadados']
		sent_id = arg['sent_id']
		map_id = arg['map_id']
		
		corresponde = False
		if limit and limit == len(output):
			break
		for token_t in available_tokens:
			token = sentence_tokens[token_t]
			try:
				if (not "-" in token.id and not '.' in token.id and eval(pesquisa)):
					corresponde = True
					text_tokens[map_id[token.id]] = "@BLUE/" + text_tokens[map_id[token.id]] + "/FONT"
					token_new_string = "@BLUE/" + token.string + "/FONT"
					tokens = tokens.replace(token.string, token_new_string)
					token.string = token_new_string

					if "token.head_token" in pesquisa and not "_token.head_token" in pesquisa:
						text_tokens[map_id[token.head_token.id]] = "@RED/" + text_tokens[map_id[token.head_token.id]] + "/FONT"
						token_new_string = "@RED/" + token.head_token.string + "/FONT"
						tokens = tokens.replace(token.head_token.string, token_new_string)
						token.head_token.string = token_new_string
						
					text_tokens[map_id[eval(arroba).id]] = "<b>" + text_tokens[map_id[eval(arroba).id]] + "</b>"
					casos.append(1)
					token_new_string = "<b>" + eval(arroba).string + "</b>"
					tokens = tokens.replace(eval(arroba).string, token_new_string)
					eval(arroba).string = token_new_string
					
			except Exception as e:
				sys.stderr.write("\n" + str(e) + ': ' + token.to_str())
				pass

		if corresponde:
			corresponde = False
			final = "# text_tokens = " + " ".join(text_tokens) + "\n" + sentence_metadados + "\n" + tokens
			output.append(final)

	return output, casos

def chunks(l, n):
	"""Yield n number of striped chunks from l."""
	for i in range(0, n):
		yield l[i::n]

#Ele só pede os inputs se o script for executado pelo terminal. Caso contrário (no caso do código ser chamado por uma página html), ele não pede os inputs, pois já vou dar a ele os parâmetros por meio da página web
if __name__ == '__main__':
	import sys
	if len(sys.argv) < 2:
		arquivoUD = input('arraste arquivo:\n').replace("'","").replace('"','').strip()
	else:
		arquivoUD = sys.argv[1]
	
	if len(sys.argv) == 3:
		criterio = int(sys.argv[2].split(" ", 1)[0])
		parametros = sys.argv[2].split(" ", 1)[1]
	else:
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
			parametros = y + '#' + str(z) + '#' + k + '#' + str(w)
			
		if criterio == 4:
			filho = input('Filho: ')
			pai = input('Pai: ')
			parametros = filho + ' :: ' + pai

		if criterio == 5:
			parametros = input("Expressão de busca:\n")

	#Chama a função principal e printo o resultado, dando a ela os parâmetros dos inputs
	principal = main(arquivoUD, criterio, parametros)
	printar = principal['output']
	
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
		#print(getDistribution(arquivoUD, parametros, criterio=criterio))
	
	print(printar)
	print("results: {}".format(principal['casos']))
	
