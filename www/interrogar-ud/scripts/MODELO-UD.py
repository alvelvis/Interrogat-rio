'''Classes:

token:
	token.id;
	token.word;
	token.lemma;
	token.upos;
	token.xpos;
	token.feats;
	token.dephead;
	token.deprel;
	token.deps;
	token.misc;
	token.head_token;
tokens: conjunto de tokens da sentença
n: número do token
tokens[n] = token

Para procurar outro token (token2) na mesma sentença e saber qual a posição dele (k):
	for k, token2 in enumerate(tokens):
		...
'''

import estrutura_ud
import sys
from datetime import datetime
import copy

conllu = sys.argv[1]
action = sys.argv[2]
issue = sys.argv[3]

headers = [x.lower() for x in open('../interrogar-ud/scripts/headers.txt', 'r').read().splitlines()]

arquivo_ud = estrutura_ud.Corpus(recursivo=True)
with open('../interrogar-ud/conllu/' + conllu, 'r') as f:
	arquivo_ud.build(f.read())

novo_inquerito = list()
sim = list()

for head in arquivo_ud.sentences:
	alterar = ''
	sent_id = "NONE"
	sentence = arquivo_ud.sentences[head]
	tokens = sentence.tokens
	if sentence.text and '# text = ' + sentence.text.lower() in headers:
		alterar = sentence.text
	if sentence.sent_id:
		sent_id = sentence.sent_id
	if alterar:
		for n, token in enumerate(tokens):

			with open('../interrogar-ud/scripts/' + issue, 'r') as f:
				codigo = [x for x in f.read().splitlines() if x.strip() and x.strip()[0] != "#"]
			
			token_var = 'token'
			for x, linha in enumerate(codigo):
				if 'for ' in linha and 'enumerate(' in linha:
					token_var = linha.split('for ')[1].split(' in ')[0].split(',', 1)[1].strip()
				elif 'for ' in linha:
					token_var = linha.split('for ')[1].split(' in ')[0].strip()
				if not 'if ' in linha and ' = ' in linha and '.' in linha:
					token_col = linha.split('.', 1)[1].split(" = ")[0].strip()
					tab = (len(linha.split('\t')) -1) * '\t'
					codigo[x] = tab + "try:\n" + tab + "\tanterior = copy.copy(" + token_var + ".to_str()[:])\n" + tab + "except:\n" + tab + "\tpass\n" + codigo[x] + "\n" + tab + "try:\n" + tab + "\tnovo_inquerito.append(alterar + '!@#' + anterior + ' --> ' + " + token_var + ".to_str().replace(" + token_var + "." + token_col + ", '<b>' + " + token_var + "." + token_col + " + '</b> (' + " + token_var + ".head_token.word + ')') + '!@#' + conllu + '!@#' + str(datetime.now()).replace(' ', '_').split('.')[0] + '!@#' + sent_id)\n" + tab + "\tsim.append(alterar + '''\n''' + 'ANTES: ' + anterior + '''\n''' + 'DEPOIS: ' + " + token_var + ".to_str().replace(" + token_var + "." + token_col + ", " + token_var + "." + token_col + " + ' (' + " + token_var + ".head_token.word + ')'))\n" + tab + "except:\n" + tab + "\tpass"

			codigo = "\n".join(codigo)
			with open("codigo", "w") as f:
				f.write(codigo)
			exec(codigo)
										
if action == 'sim': open('../interrogar-ud/scripts/sim.txt', 'w').write('\n\n'.join(sim))
if action == 'exec': open('../interrogar-ud/scripts/novos_inqueritos.txt', 'w').write('\n'.join(novo_inquerito))
if action == 'exec':
	with open('../interrogar-ud/conllu/' + conllu + '_script', 'w') as f:
		f.write(arquivo_ud.to_str())
