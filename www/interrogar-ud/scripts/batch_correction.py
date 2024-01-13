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

import sys, re
sys.path.append("./cgi-bin")
import estrutura_ud
from utils import fastsearch, col_to_idx, query_is_python
from datetime import datetime
import charset_normalizer
import pandas as pd
import copy
import html
import uuid

conllu = sys.argv[1]
action = sys.argv[2]
script_file = sys.argv[3]
script_name = sys.argv[4]
interrogatorio = sys.argv[5]
occ = int(sys.argv[6]) if sys.argv[5] not in fastsearch else ""
href = sys.argv[7] if sys.argv[5] not in fastsearch else ""
query = sys.argv[8]
full_query = sys.argv[9] if query_is_python(sys.argv[9]) else ""

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

srcfile = './interrogar-ud/scripts/' + script_file
file_content = str(charset_normalizer.from_path(srcfile).best())
with open(srcfile, 'w', encoding='utf-8') as e:
	e.write(file_content)
codigo = [x for x in file_content.splitlines() if x.strip() and x.strip()[0] != "#"]

keywords = []
for linha in codigo:
	if 'if ' in linha:
		keywords.extend([x.replace("^(", "").replace(")$", "") for x in re.findall(r'"([^"]*)"', linha) if not x.startswith(")") and not x.endswith("(")])#[x.replace("\\(", "<abreparenteses>").replace("\\)", "<fechaparenteses>").replace("(", "").replace(")", "").replace("<abreparenteses>", "\\(").replace("<fechaparenteses>", "\\)") for x in re.findall(r'"([^"]*)"', linha)])

arquivo_ud = estrutura_ud.Corpus(recursivo=True, keywords=keywords, any_of_keywords=["# sent_id = %s\n" % x for x in headers])
arquivo_ud.load('./interrogar-ud/conllu/' + conllu)

token_var = 'token'
date = datetime.now()
_id = str(uuid.uuid4())
for x, linha in enumerate(codigo):
	if linha.strip() and not 'if ' in linha and ' = ' in linha and '.' in linha.split(" = ")[0] and not 'for ' in linha and not 'else:' in linha and not 'elif ' in linha:
		token_var = linha.split(" = ")[0].strip().rsplit(".", 1)[0].strip()
		token_col = linha.split(" = ")[0].strip().rsplit(".", 1)[1].strip()
		if token_col in col_to_idx:
			tab = (len(linha.split('\t')) -1) * '\t'
			codigo[x] = tab + "try:\n" + \
						tab + "\tanterior = copy.copy(" + token_var + ".to_str()[:])\n" + \
						tab + "\t" + codigo[x].strip() + "\n" + \
						tab + f"\tif anterior != {token_var}.to_str():\n" + \
						tab + f'''\t\tnew_inquiries.append({{
										'_id': "{_id}",
										'date': "{date.timestamp()}",
										'tag': "{script_name}",
										'conllu': "{conllu.split('.conllu')[0]}",
										'text': " ".join([x.word if x.id != {token_var}.id else "<b>%s</b>" % x.word for x in sentence.tokens if not '-' in x.id]),
										'sent_id': sentence.sent_id,
										'before': anterior, 
										'after': {token_var}.to_str(),
										'col': "{token_col}",
										'head': get_head({token_var}, sentence), 
										'interrogatorio': "{interrogatorio}",
										'occurrences': "{occ}",
										'href': "{href}",
										'query': query,
										'full_query': full_query,
										}})\n''' + \
						tab + "except Exception as e:\n" + \
						tab + "\tsys.stderr.write(str(e))"

with open("./cgi-bin/debug_batch_correction.txt", "w") as f:
	f.write("\n".join(codigo))

codigo = "\n".join(codigo)

new_inquiries = []
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
			with open("./cgi-bin/debug_batch_correction_error.log", "w") as f:
				f.write(html.escape(str(e)))
			exit()
										
df = pd.DataFrame(new_inquiries)
df.to_csv("./interrogar-ud/batch_correction_simulation.csv")

if action == 'exec':
	with open('./interrogar-ud/conllu/' + conllu + '_script', 'w') as f:
		f.write(arquivo_ud.to_str())
