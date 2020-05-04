# -*- coding: UTF-8 -*-
import re
import copy
import sys
import time
from functions import tabela as tabelaf, cleanEstruturaUD
import cgi
import html as web

different_distribution = ["dependentes", "children"]

def getDistribution(arquivoUD, parametros, criterio=5, coluna="lemma", filtros=[], sent_id=""):
	import estrutura_ud

	if not isinstance(arquivoUD, dict):
		sentences = main(arquivoUD, criterio, parametros, sent_id=sent_id, fastSearch=True)['output']
	else:
		sentences = arquivoUD['output']
		
	corpus = list()
	for sentence in sentences:
		sent = estrutura_ud.Sentence()
		sent.build(sentence['resultado'].replace(f"@YELLOW/", "").replace(f"@RED/", "").replace(f"@CYAN/", "").replace(f"@BLUE/", "").replace(f"@PURPLE/", "").replace("/FONT", ""))
		if sent.sent_id not in filtros:
			corpus.append(sent)
	
	dist = list()
	all_children = {}
	for sentence in corpus:
		for t, token in enumerate(sentence.tokens):
			if '<b>' in token.to_str() or "</b>" in token.to_str():
				if not coluna in different_distribution:
					dist.append(token.col.get(coluna))
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
						dist.append(" ".join(children_list))
						if children_list:
							if not " ".join(children_list) in all_children:
								all_children[" ".join(children_list)] = []
							all_children[" ".join(children_list)].append(sentence.sent_id)


	dicionario = dict()
	for entrada in dist:
		#entrada = entrada.replace("<b>", "").replace("</b>", "")
		if not entrada in dicionario: dicionario[entrada] = 1
		else: dicionario[entrada] += 1

	lista = list()
	for entrada in dicionario:
		lista.append((entrada, dicionario[entrada]))

	freq = dict()
	for entrada in dicionario:
		if not dicionario[entrada] in freq: freq[dicionario[entrada]] = 1
		else: freq[dicionario[entrada]] += 1
	lista_freq = list()
	for entrada in freq:
		lista_freq.append((entrada, freq[entrada]))

	return {"all_children": all_children, "lista": lista, "dist": len(dist)}

#Crio a função que vai ser chamada seja pelo HTML ou seja pelo terminal
def main(arquivoUD, criterio, parametros, limit=0, sent_id="", fastSearch=False, separate=False):
	parametros = parametros.strip()
	pesquisa = ""

	if criterio in [1]:
		import estrutura_ud
	
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
		with open(arquivoUD) as f:
			for line in f:
				if line.strip():
					sentence += line
				else:
					if limit and len(output) == limit:
						break
					regex = re.findall('(' + parametros + ')', sentence)
					if regex:
						casos += len(regex)
						new_sentence = re.sub('(' + parametros + ')', r'<b>\1</b>', sentence)
						tokens = list()
						header = '!@#'
						for linha in new_sentence.splitlines():
							if '# text = ' in linha:
								header = linha
							if 'b>' in linha and '\t' in linha:
								tokens.append(linha.split('\t')[1].replace('<b>','').replace('</b>',''))
						header2 = header
						for token in tokens:
							header2 = re.sub(r'\b' + re.escape(token) + r'\b', '<b>' + token + '</b>', header2)
						for reg in regex:
							if not isinstance(reg, str):
								for i, grupo in enumerate(reg):
									if i != 0:
										if grupo and i-1 < len(tabela):
											if '\t' in grupo:
												token = grupo.split('\t')[1]
											header2 = re.sub(r'\b' + re.escape(token) + r'\b', tabela[i-1] + token + '/FONT', header2)
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
#		pesquisa = pesquisa.replace("== int(", "==int(")
		pesquisa = re.sub(r'token\.([1234567890])', r'\1', pesquisa)

		pesquisa = re.sub(r'(\S+)\s==\s(\".*?\")', r'any( re.search( r"^" + r\2 + r"$", x ) for x in \1.split("|") )', pesquisa)
		pesquisa = re.sub(r'(\S+)\s===\s(\".*?\")', r'all( re.search( r"^" + r\2 + r"$", x ) for x in \1.split("|") )', pesquisa)
		pesquisa = re.sub(r'(\S+)\s!=\s(\".*?\")', r'not any( re.search( r"^" + r\2 + r"$", x ) for x in \1.split("|") )', pesquisa)
		pesquisa = re.sub(r'(\S+)\s!==\s(\".*?\")', r'not all( re.search( r"^" + r\2 + r"$", x ) for x in \1.split("|") )', pesquisa)
		pesquisa = pesquisa.strip()

		if (".id" in pesquisa or ".dephead" in pesquisa) and (not "int(" in pesquisa) and ("<" in pesquisa or ">" in pesquisa):
			pesquisa = re.sub(r"(\b\S+\.(id|dephead)\b)", r"int(\1)", pesquisa)

		identificador = "token"

		if parametros[0] == "@":
			parametros = parametros[1:]
		
		arroba = parametros.split(" ")[0] if not ' @' in parametros else parametros.rsplit(" @", 1)[1].replace("int(", "").split(")")[0].split(" ")[0].replace("(", "")
		arroba = "token." + arroba
		arroba = arroba.replace("token.token", "token")
		arroba = arroba.rsplit(".", 1)[0]

		agilizar = re.findall(r'"([^"]*)"', parametros)# if any(x in parametros for x in [".lemma", ".word", ".misc", ".feats", ".deps", ".xpos"]) else []

#		with open("interrogar_UD.txt", "w") as f:
#			f.write(pesquisa)

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
		for sentence in corpus.sentences.values():
			if limit and limit == len(output):
				break
			condition = "global sim; global sentence2; sim = 0; sentence2 = copy.copy(sentence); sentence2.print = sentence2.tokens_to_str();"
			
			condition += '''
for ''' + identificador + ''' in sentence.tokens:
	try:
		if not "-" in '''+identificador+'''.id and (''' + pesquisa + ''') :
			sentence2.metadados['corresponde'] = 1
			sentence2.metadados['text'] = re.sub(r'\\b(' + re.escape('''+ identificador +'''.word) + r')\\b', r"@RED/\\1/FONT", sentence2.metadados['text'], flags=re.IGNORECASE|re.MULTILINE)
			sentence2.print = sentence2.print.replace('''+ identificador +'''.to_str(), "@RED/" + '''+ identificador +'''.to_str() + "/FONT")
	'''#try por causa de não ter um next_token no fim de sentença, por ex.
			if identificador + ".head_token" in pesquisa:
				condition += '''
			sentence2.metadados['text'] = re.sub(r'\\b(' + re.escape('''+ identificador +'''.head_token.word) + r')\\b', r"@BLUE/\\1/FONT", sentence2.metadados['text'], flags=re.IGNORECASE|re.MULTILINE)
			sentence2.print = sentence2.print.replace('''+ identificador +'''.head_token.to_str(), "@BLUE/" + '''+ identificador +'''.head_token.to_str() + "/FONT")'''
			
			condition += '''
			sentence2.metadados['text'] = re.sub(r'\\b(' + re.escape('''+ arroba +'''.word) + r')\\b', r"<b>\\1</b>", sentence2.metadados['text'], flags=re.IGNORECASE|re.MULTILINE)
			'''

			exec(condition + '''
			casos.append(1)
			arroba = '''+arroba+'''.id
			sentence2.print = sentence2.print.splitlines()
			for l, linha in enumerate(sentence2.print):
				if linha.split("\\t")[0] == arroba or ("/" in linha.split("\\t")[0] and linha.split("\\t")[0].split("/")[1] == arroba):
					sentence2.print[l] = "<b>" + sentence2.print[l] + "</b>"
			sentence2.print = "\\n".join(sentence2.print)

			if separate:
				sentence2.metadados.pop('corresponde', None)
				final = sentence2.metadados_to_str() + "\\n" + sentence2.print
				output.append(final)
			
	except Exception as e:
		print(e)
		pass
if 'corresponde' in sentence2.metadados and not separate:
	sentence2.metadados.pop('corresponde', None)
	final = sentence2.metadados_to_str() + "\\n" + sentence2.print
	output.append(final)''')
		sys.stderr.write("\ncritério 5: " + str(time.time() - start) + "\n")
		casos = len(casos)
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
			anotado.build(cgi.escape(final.replace('<b>', '@BOLD').replace('</b>', '/BOLD').replace('<font color=' + tabelaf['yellow'] + '>', '@YELLOW/').replace('<font color=' + tabelaf['red'] + '>', '@RED/').replace('<font color=' + tabelaf['cyan'] + '>', '@CYAN/').replace('<font color=' + tabelaf['blue'] + '>', '@BLUE/').replace('<font color=' + tabelaf['purple'] + '>', '@PURPLE/').replace('</font>', '/FONT')))		
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
	
