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
import sys, os, re
from datetime import datetime
import copy
from chardet import detect
import html


# get file encoding type
def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']

conllu = sys.argv[1]
action = sys.argv[2]
issue = sys.argv[3]

headers = [x.lower() for x in open('../interrogar-ud/scripts/headers.txt', 'r').read().splitlines()]

arquivo_ud = estrutura_ud.Corpus(recursivo=True)
arquivo_ud.load('../interrogar-ud/conllu/' + conllu)

novo_inquerito = list()
sim = list()

def append_to(original, s, delimiter="|"):
	original = original.split(delimiter)
	novosFeats = s.split(delimiter)
	novosFeats += [x for x in original if x != "_" and not any(y.split("=")[0] == x.split("=")[0] for y in novosFeats)]

	return delimiter.join(sorted(novosFeats))

def remove_from(original, s, delimiter="|"):
	original = original.split(delimiter)
	deletedFeats = s.split(delimiter)
	original = [x for x in original if x not in deletedFeats and not any(y == x.split("=")[0] for y in deletedFeats)]
	if not original: original = ["_"]

	return delimiter.join(sorted(original))

def get_head(tok, tokens):
	for token in tokens:
		if token.id == tok.dephead:
			return token.word
	return "_"

srcfile = '../interrogar-ud/scripts/' + issue
trgfile = 'codification'
from_codec = get_encoding_type(srcfile)
with open(srcfile, 'r', encoding=from_codec) as f, open(trgfile, 'w', encoding='utf-8') as e:
	text = f.read() # for small files, for big use chunks
	e.write(text)
os.remove(srcfile) # remove old encoding file
os.rename(trgfile, srcfile) # rename new encoding
with open(srcfile, 'r') as f:
	codigo = [x for x in f.read().splitlines() if x.strip() and x.strip()[0] != "#"]

token_var = 'token'
for x, linha in enumerate(codigo):
	if linha.strip() and not 'if ' in linha and ' = ' in linha and '.' in linha and not 'for ' in linha:
		token_var = linha.split(" = ")[0].strip().rsplit(".", 1)[0].strip()
		token_col = linha.split(" = ")[0].strip().rsplit(".", 1)[1].strip()
		tab = (len(linha.split('\t')) -1) * '\t'
		codigo[x] = tab + "try:\n" + tab + "\tanterior = copy.copy(" + token_var + ".to_str()[:])\n" + tab + "except:\n" + tab + "\tpass\n" + codigo[x] + "\n" + tab + "try:\n" + tab + "\tnovo_inquerito.append(alterar + '!@#' + anterior + ' --> ' + " + token_var + ".to_str().replace(" + token_var + "." + token_col + ", '<b>' + " + token_var + "." + token_col + " + '</b> (' + get_head(" + token_var + ", tokens) + ')') + '!@#' + conllu + '!@#' + str(datetime.now()).replace(' ', '_').split('.')[0] + '!@#' + sent_id)\n" + tab + "\tsim.append(re.sub(r'\\b' + " + token_var + ".word + r'\\b', '<b>' + " + token_var + ".word + '</b>', alterar) + '''\n''' + 'ANTES: ' + html.escape(anterior) + '''\n''' + 'DEPOIS: ' + html.escape(" + token_var + ".to_str().replace(" + token_var + "." + token_col + ", " + token_var + "." + token_col + " + ' (' + get_head(" + token_var + ", tokens) + ')')))\n" + tab + "except:\n" + tab + "\tpass"

with open("codigo", "w") as f:
	f.write("\n".join(codigo))

codigo = "\n".join(codigo)

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
			try:
				exec(codigo)
			except Exception as e:
				with open("../cgi-bin/error.log", "w") as f:
					f.write(html.escape(str(e)))
					exit()
										
if action == 'sim': open('../interrogar-ud/scripts/sim.txt', 'w').write('\n\n'.join(sim))
if action == 'exec':
	with open('../interrogar-ud/scripts/novos_inqueritos.txt', 'w') as f:
		f.write('\n'.join(novo_inquerito))
	with open('../interrogar-ud/conllu/' + conllu + '_script', 'w') as f:
		f.write(arquivo_ud.to_str())
