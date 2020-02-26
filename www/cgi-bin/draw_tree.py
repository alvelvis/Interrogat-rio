#!/usr/bin/python3

import estrutura_ud
import os
import cgi, cgitb
cgitb.enable()

print('Content-type:text/html\n\n')	

class Token:
	
	def __init__(self, separator='\t'):
		self.id = 0
		self.word = "_"
		self.lemma = "_"
		self.upos = "_"
		self.xpos = "_"
		self.feats = "_"
		self.dephead = 0
		self.deprel = "_"
		self.deps = "_"
		self.misc = "_"
		self.children = []
		self.separator = separator

	def build(self, txt):
		coluna = txt.split(self.separator)
		try:
			self.id = int(coluna[0])
		except:
			self.id = -1
		self.word = coluna[1]
		self.lemma = coluna[2]
		self.upos = coluna[3]
		self.xpos = coluna[4]
		self.feats = coluna[5]
		try:
			self.dephead = int(coluna[6])
		except:
			self.dephead = -1
		self.deprel = coluna[7]
		self.deps = coluna[8]
		self.misc = coluna[9]

		if self.dephead == 0:
			self.dephead == self.id

	def to_str(self):
		return self.separator.join([str(self.id), self.word, self.lemma, self.upos, self.xpos, self.feats, str(self.dephead), self.deprel, self.deps, self.misc])


class Stand:

	def __init__(self, separator="\n"):
		self.roots = []
		self.tokens = {}
		self.separator = separator
		
	def build(self, txt):
		self.tokencs = {}
		tok_lines = txt.split(self.separator)

		for tok_line in tok_lines:
			tok_line = tok_line.strip()
			if tok_line:
				tok = Token()
				tok.build(tok_line)
				self.tokens[tok.id] = tok
				if tok.dephead == 0:
					self.roots.append(tok)

		for tok_id in self.tokens:
			tok = self.tokens[tok_id]
			if tok.dephead > 0:
				self.tokens[tok.dephead].children.append(tok)

	def _to_str(self, dephead, inner=0, child=False):
		space = "   " * inner
		last = '└' if child else '─'
		rep = ['{:4} '.format(str(dephead.id)) + space + ' ' + last + ' "' + " ".join([dephead.word + '"', dephead.upos, dephead.deprel])]

		for child in dephead.children:
			rep.append(self._to_str(child, inner+1, child=True))

		return "\n".join(rep)

	def to_str(self):
		every_tree = ""

		for root in self.roots:
			every_tree += self._to_str(root) + "\n"

		every_tree += "\n"
		return every_tree


class Forest:

	def __init__(self, separator='\n\n'):
		self.stands = []
		self.separator = separator
		self.remaining_tokens_str = set()

	def build(self, txt):
		self.stands = []
		tree_txts = txt.split(self.separator)

		for tr_txt in tree_txts:
			tr_txt = tr_txt.strip()
			if tr_txt:
				doc_stand = Stand()
				doc_stand.build(tr_txt)
				self.stands.append(doc_stand)

	def to_str(self):
		every_stand = ""
		for stand in self.stands:
			every_stand += stand.to_str()

		return every_stand


if os.environ['REQUEST_METHOD'] == 'POST':
	form = cgi.FieldStorage()

	with open('../interrogar-ud/conllu/' + form['conllu'].value, 'r') as f:
		arquivo = f.read()

	conllu = estrutura_ud.Corpus(recursivo=False)
	conllu.build(arquivo)

	sentence = conllu.sentences[form['text'].value] if 'text' in conllu.sentences else conllu.sentences[form['sent_id'].value]

	forest = Forest()
	forest.build(sentence.tokens_to_str())

	print('''<html><head><title class="translateHtml">Visualizar árvore: Interrogatório</title><script src=\"../../interrogar-ud/jquery-latest.js\"></script><script src=\"../../interrogar-ud/resultados.js?version=15\"></script><meta charset="UTF-8" name="viewport"><style>body { width: 90%; margin: 20px auto; }</style></head><body><h1 class="translateHtml">Visualizar árvore</h1><hr><a href="#" class="translateHtml" onclick="window.close()">Fechar</a><br><br>
	''' + form['conllu'].value + "<br><br>" + sentence.text + '<pre style="font-size: 14px; line-height: 1.5;">' + forest.to_str() + '</pre></body></html>')
