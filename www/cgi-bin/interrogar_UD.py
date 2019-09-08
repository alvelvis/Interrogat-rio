# -*- coding: UTF-8 -*-
import re
import copy
import sys

#Crio a função que vai ser chamada seja pelo HTML ou seja pelo terminal
def main(arquivoUD, criterio, parametros):
	parametros = parametros.strip()
	
	#Lê o arquivo UD
	if criterio in [1, 2, 3, 4]:
		import estrutura_dados
		qualquercoisa = estrutura_dados.LerUD(arquivoUD)

	if criterio in [5]:
		import estrutura_ud
		with open(arquivoUD, "r") as f:
			if "head_token" in parametros or "next_token" in parametros or "previous_token" in parametros:
				#qtd = len(parametros.split("head_token")) -1 + len(parametros.split("previous_token")) -1 + len(parametros.split("next_token")) -1
				corpus = estrutura_ud.Corpus(recursivo=True)
			else:
				corpus = estrutura_ud.Corpus(recursivo=False)
			corpus.build(f.read())
			

	#Cria a lista que vai ser enviada seja ao terminal ou ao HTML
	output = list()
	casos = 0

	#Regex
	tabela = ['@YELLOW/','@PURPLE/','@BLUE/','@RED/','@CYAN/']
	
	if criterio == 1:
		for a, sentence in enumerate(qualquercoisa):
			sentence2 = sentence
			for b, linha in enumerate(sentence):
				linha2 = linha
				if isinstance(linha2, list):
					sentence2[b] = "\t".join(sentence2[b])
			sentence2 = "\n".join(sentence2)
			regex = re.search(parametros, sentence2, flags=re.IGNORECASE|re.MULTILINE)
			if regex:
				casos += len(re.findall(parametros, sentence2, flags=re.IGNORECASE|re.MULTILINE))
				cores = len(regex.groups())
				new_sentence = re.sub('(' + parametros + ')', r'<b>\1</b>', sentence2, flags=re.IGNORECASE|re.MULTILINE)
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
				for i in range(cores):
					if regex[i+1] != None and i < len(tabela):
						token = regex[i+1]
						if '\t' in regex[i+1]:
							token = regex[i+1].split('\t')[1]
							header2 = re.sub(r'\b' + re.escape(token) + r'\b', tabela[i] + token + '/FONT', header2)
				new_sentence = new_sentence.replace(header, header2)
				output.append(new_sentence.splitlines())

	#If critério 2
	if criterio == 2:

		#Variáveis
		y = parametros.split('#')[0].strip()
		z = int(parametros.split('#')[1])
		k = [x.strip() for x in parametros.split('#')[2].split('|')]
		w = int(parametros.split('#')[3])
		for sentence in qualquercoisa:
			achei = 'nãoachei'
			descarta = False
			for i, linha in enumerate(sentence):
				if isinstance(linha, list):
					#print(linha)
					if y == linha[z-1]:
						achei = linha[0]
						token = linha[1]
						sentence[i] = '<b>' + '\t'.join(sentence[i]) + '</b>'
						sentence[i] = sentence[i].split('\t')
						#break
			if achei != 'nãoachei':
				for i, linha in enumerate(sentence):
					if '# text' in linha:
						sentence[i] = re.sub(r'\b' + re.escape(token) + r'\b', '<b>' + token + '</b>', sentence[i])

			if achei != 'nãoachei':
				for linha in sentence:
					if isinstance(linha, list):
						for k_subitem in k:
							if achei == linha[6] and k_subitem == linha[z-1]:
								descarta = True
				if descarta == False:
					output.append(sentence)
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
		casos = 0

		pesquisa = pesquisa.replace("'", '"')
		pesquisa = pesquisa.replace("=", " = ")
		pesquisa = pesquisa.replace(" =  = ", " = ")
		pesquisa = pesquisa.replace("! =", "!=")
		pesquisa = pesquisa.replace(" = ", " == ")
		pesquisa = pesquisa.replace(" @", " ")
		pesquisa = pesquisa.replace("  ", " ").strip()
		if pesquisa[0] == "@": pesquisa = pesquisa[1:]
		pesquisa = pesquisa.replace(" == ", " == token.")
		pesquisa = pesquisa.replace(" != ", " != token.")
		pesquisa = pesquisa.replace(" & ", " and ")
		pesquisa = "token." + pesquisa
		pesquisa = pesquisa.replace(" and ", " and token.")
		pesquisa = pesquisa.replace(" or ", " or token.")
		pesquisa = pesquisa.replace(" in ", " in token.")
		pesquisa = pesquisa.replace('token."', '"')
		pesquisa = pesquisa.replace('token.[', '[')
		pesquisa = pesquisa.replace('token.(', '(')
		pesquisa = pesquisa.replace('token.token.', 'token.')
		pesquisa = pesquisa.replace('.lower ', '.lower() ')
		pesquisa = pesquisa.replace('.upper ', '.upper() ')
		pesquisa = re.sub(r'token\.([1234567890])', r'\1', pesquisa)
		pesquisa = re.sub(r'token\.r\"(.*?)\"\s+in\s+(.*?)(\s)', r're.search(r"\1", \2)\3', pesquisa)

		if (".id" in pesquisa or ".dephead" in pesquisa) and (not "int(" in pesquisa):
			pesquisa = re.sub(r"(\b\S+\.(id|dephead)\b)", r"int(\1)", pesquisa)

		identificador = "token"
		#identificador = pesquisa.split("head_token")[0].split("next_token")[0].split("previous_token")[0].split(".")[0].strip().replace("  ", " ").replace("int(", "").split(")")[0].replace("(", "")
		#if " in " in identificador: identificador = identificador.split(" in ")[1]
		#if "@" in identificador: identificador = identificador.split("@")[1]

		if " @" in parametros:
			if parametros[0] == "@": parametros = parametros[1:]
			arroba = "token." + parametros.split(" @")[1].strip().replace("int(", "").split(")")[0].split(" ")[0].rsplit(".", 1)[0].replace("(", "")
		else:
			arroba = identificador
		if " in " in arroba: arroba = arroba.split(" in ")[1]

		with open("expressao_busca.txt", "w") as f:
			f.write(f"parametro: {parametros}\npesquisa: {pesquisa}\narroba: {arroba}")

		agilizar = pesquisa.split('"')[1].split('"')[0] if '"' in pesquisa and not "re.search" in pesquisa else ""
		agilizado = [[x, y] for x, y in corpus.sentences.items() if agilizar in y.to_str()] if agilizar else corpus.sentences.items()
		# print(agilizado)
		# print(pesquisa)
		# print(arroba)
		# exit()

		for sentid, sentence in agilizado:
			condition = "global sim; global sentence2; sim = 0; sentence2 = copy.copy(sentence); sentence2.print = sentence2.tokens_to_str()"
			
			condition += '''
for ''' + identificador + ''' in sentence.tokens:
	try:
		if not "-" in '''+identificador+'''.id and (''' + pesquisa + ''') :
			sentence2.metadados['text'] = re.sub(r'\\b(' + re.escape('''+ identificador +'''.word) + r')\\b', r"@RED/\\1/FONT", sentence2.metadados['text'], flags=re.IGNORECASE|re.MULTILINE)
			sentence2.print = sentence2.print.replace('''+ identificador +'''.to_str(), "@RED/" + '''+ identificador +'''.to_str() + "/FONT")
	'''#try por causa de não ter um next_token no fim de sentença, por ex.
			if identificador + ".head_token" in pesquisa:
				condition += '''
			sentence2.metadados['text'] = re.sub(r'\\b(' + re.escape('''+ identificador +'''.head_token.word) + r')\\b', r"@BLUE/\\1/FONT", sentence2.metadados['text'], flags=re.IGNORECASE|re.MULTILINE)
			sentence2.print = sentence2.print.replace('''+ identificador +'''.head_token.to_str(), "@BLUE/" + '''+ identificador +'''.head_token.to_str() + "/FONT")'''
			
			condition += '''
			sentence2.metadados['text'] = re.sub(r'\\b(' + re.escape('''+ arroba +'''.word) + r')\\b', r"<b>\\1</b>", sentence2.metadados['text'], flags=re.IGNORECASE|re.MULTILINE)
			final = sentence2.metadados_to_str() + "\\n" + sentence2.print
			final = final.splitlines()
			arroba = '''+arroba+'''.id
			for l, linha in enumerate(final):
				if linha.split("\\t")[0] == arroba or ("/" in linha.split("\\t")[0] and linha.split("\\t")[0].split("/")[1] == arroba):
					final[l] = "<b>" + final[l] + "</b>"
			final = "\\n".join(final)'''

			exec(condition + '''
			output.append(final)
	except:
		pass''')
		
		for a, sentence in enumerate(output):
			output[a] = sentence.splitlines()
			for b, linha in enumerate(output[a]):
				output[a][b] = linha.split("\t")

	#Transforma o output em lista de sentenças (sem splitlines e sem split no \t)
	for a, sentence in enumerate(output):
		for b, linha in enumerate(sentence):
			if isinstance(linha, list):
				sentence[b] = "\t".join(sentence[b])
		output[a] = "\n".join(sentence)

	return {'output': output, 'casos': casos}

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
	
	print(printar)

