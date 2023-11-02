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

import sys, os, re
sys.path.append("./cgi-bin")
import estrutura_ud
from datetime import datetime
import copy
from chardet import detect
import html
import multiprocessing


# get file encoding type
def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']

conllu = sys.argv[1]
action = sys.argv[2]
issue = sys.argv[3]

with open('./interrogar-ud/scripts/headers.txt', 'r') as f:
	headers = f.read().splitlines()

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

def get_head(tok, sentence):
	return sentence.tokens[sentence.map_token_id[tok.dephead]].word if tok.dephead in sentence.map_token_id else "_"

def regex(exp, col):
    return re.search(r'^(' + exp + r")$", col)

srcfile = './interrogar-ud/scripts/' + issue
trgfile = 'codification'
from_codec = get_encoding_type(srcfile)
with open(srcfile, 'r', encoding=from_codec) as f, open(trgfile, 'w', encoding='utf-8') as e:
	text = f.read() # for small files, for big use chunks
	e.write(text)
os.remove(srcfile) # remove old encoding file
os.rename(trgfile, srcfile) # rename new encoding
with open(srcfile, 'r') as f:
	codigo = [x for x in f.read().splitlines() if x.strip() and x.strip()[0] != "#"]

keywords = []
for linha in codigo:
	if 'if ' in linha:
		keywords.extend([x.replace("^(", "").replace(")$", "") for x in re.findall(r'"([^"]*)"', linha) if not x.startswith(")") and not x.endswith("(")])#[x.replace("\\(", "<abreparenteses>").replace("\\)", "<fechaparenteses>").replace("(", "").replace(")", "").replace("<abreparenteses>", "\\(").replace("<fechaparenteses>", "\\)") for x in re.findall(r'"([^"]*)"', linha)])

arquivo_ud = estrutura_ud.Corpus(recursivo=True, keywords=keywords, any_of_keywords=headers)
arquivo_ud.load('./interrogar-ud/conllu/' + conllu)

token_var = 'token'
for x, linha in enumerate(codigo):
	if linha.strip() and not 'if ' in linha and ' = ' in linha and '.' in linha.split(" = ")[0] and not 'for ' in linha and 'token.' in linha and not 'else:' in linha and not 'elif ' in linha:
		token_var = linha.split(" = ")[0].strip().rsplit(".", 1)[0].strip()
		token_col = linha.split(" = ")[0].strip().rsplit(".", 1)[1].strip()
		tab = (len(linha.split('\t')) -1) * '\t'
		codigo[x] = tab + "try:\n" + \
					tab + "\tanterior = copy.copy(" + token_var + ".to_str()[:])\n" + \
					tab + "except Exception as e:\n" + \
					tab + "\tsys.stderr.write(str(e))\n" + \
					codigo[x] + "\n" + \
					tab + "try:\n" + \
					tab + "\tif anterior != " + token_var + ".to_str():\n" + \
					tab + "\t\tnovo_inquerito.append(' '.join([(x.word if x.id != " + token_var + ".id else '<b>{}</b>'.format(x.word)) for x in sentence.tokens if not '-' in x.id]) + \
													'!@#' + anterior + ' --> ' + " + token_var + ".to_str() + ' (head: ' + get_head(" + token_var + ", sentence) + ')' + \
													'!@#' + conllu + \
													'!@#' + str(datetime.now()).replace(' ', '_').split('.')[0] + \
													'!@#' + sentence.sent_id)\n" + \
					tab + "\t\tsim.append(' '.join([(html.escape(x.word) if x.id != " + token_var + ".id else '<b>{}</b>'.format(html.escape(x.word))) for x in sentence.tokens if not '-' in x.id]) + '''\n''' + \
											'ANTES: ' + html.escape(anterior) + '''\n''' + \
											'DEPOIS: ' + html.escape(" + token_var + ".to_str() + ' (head: ' + get_head(" + token_var + ", sentence) + ')'))\n" + \
					tab + "except Exception as e:\n" + \
					tab + "\tsys.stderr.write(str(e))"

with open("./cgi-bin/codigo.txt", "w") as f:
	f.write("\n".join(codigo))

codigo = "\n".join(codigo)

for head in headers:
	sentence = arquivo_ud.sentences[head]
	tokens = sentence.tokens
	for n, token in enumerate(tokens):
		try:
			exec(codigo)
			#sys.stderr.write(codigo)
			#exit()
		except AttributeError as e:
			sys.stderr.write("\n%s" % str(e))
			pass
		except Exception as e:
			with open("./cgi-bin/error.log", "w") as f:
				f.write(html.escape(str(e)))
			exit()
										
if action == 'sim':
	with open('./interrogar-ud/scripts/sim.txt', 'w') as f:
		f.write('\n\n'.join(sim))
if action == 'exec':
	with open('./interrogar-ud/scripts/novos_inqueritos.txt', 'w') as f:
		f.write('\n'.join(novo_inquerito))
	with open('./interrogar-ud/conllu/' + conllu + '_script', 'w') as f:
		f.write(arquivo_ud.to_str())
