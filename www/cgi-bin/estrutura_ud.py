class Token:
	
	def __init__(self, separator='\t', sent_id="NONE", text="NONE"):
		self.id = "0"
		self.word = "_"
		self.lemma = "_"
		self.upos = "_"
		self.xpos = "_"
		self.feats = "_"
		self.dephead = "0"
		self.deprel = "_"
		self.deps = "_"
		self.misc = "_"
		self.children = []
		self.separator = separator
		self.col = dict()
		self.sent_id = sent_id
		self.text = text
		self.color = ""

	def build(self, txt):
		coluna = txt.split(self.separator)

		self.id = coluna[0]
		self.word = coluna[1]
		self.lemma = coluna[2]
		self.upos = coluna[3]
		self.xpos = coluna[4]
		self.feats = coluna[5]
		self.dephead = coluna[6]
		self.deprel = coluna[7]
		self.deps = coluna[8]
		self.misc = coluna[9]
		self.col["id"] = self.id
		self.col["word"] = self.word
		self.col["lemma"] = self.lemma
		self.col["upos"] = self.upos
		self.col["xpos"] = self.xpos
		self.col["feats"] = self.feats
		self.col["dephead"] = self.dephead
		self.col["deprel"] = self.deprel
		self.col["deps"] = self.deps
		self.col["misc"] = self.misc

	def to_str(self):
		return self.separator.join([self.id, self.word, self.lemma, self.upos, self.xpos, self.feats, self.dephead, self.deprel, self.deps, self.misc])


class Sentence:

	def __init__(self, separator="\n", recursivo=0):
		self.text = ""
		self.sent_id = ""
		self.source = ""
		self.id = ""
		self.metadados = {}
		self.recursivo = recursivo

		f = "_\t" * 10
		self.default_token = Token()
		self.default_token.build(f.rsplit('\t', 1)[0])

		self.tokens = list()
		self.tokens_incompletos = list()
		self.separator = separator


	def get_head(self, token):
		next_t = False
		previous_t = False
		for tok in self.tokens:
			if tok.id == token.dephead:
				token.head_token = tok

			if not "-" in token.id and not "-" in tok.id and not "/" in token.id and not "/" in tok.id:
				if int(token.id) == int(tok.id) - 1:
					token.next_token = tok
					next_t = True
				if int(token.id) == int(tok.id) + 1:
					token.previous_token = tok
					previous_t = True
			if next_t and previous_t:
				break
		if not next_t:
			token.next_token = self.default_token
		if not previous_t:
			token.previous_token = self.default_token

		return token

	def build(self, txt):
		if '# text = ' in txt:
			self.text = txt.split('# text = ')[1].split('\n')[0]
			self.metadados['text'] = self.text
		if '# sent_id = ' in txt:
			self.sent_id = txt.split('# sent_id = ')[1].split('\n')[0]
			self.metadados['sent_id'] = self.sent_id
		if '# source = ' in txt:
			self.source = txt.split('# source = ')[1].split('\n')[0]
			self.metadados['source'] = self.source
		if '# id = ' in txt:
			self.id = txt.split('# id = ')[1].split('\n')[0]
			self.metadados["id"] = self.id
		
		tokens_incompletos = list()
		for linha in txt.split(self.separator):
			if linha and "#" == linha[0] and "=" in linha:
				identificador = linha.split("#", 1)[1].split('=', 1)[0].strip()
				if identificador not in ["text", "sent_id", "source", "id"]:
					valor = linha.split('=', 1)[1].strip()
					self.metadados[identificador] = valor
			if "\t" in linha:
				tok = Token(sent_id = self.sent_id, text = self.text)
				tok.build(linha)
				tok.head_token = self.default_token
				tok.next_token = self.default_token
				tok.previous_token = self.default_token
				if self.recursivo == 0: self.tokens.append(tok)
				else: self.tokens_incompletos.append(tok)

		'''if not self.recursivo:
			for token in self.tokens:
				for _token in self.tokens:
					if token.dephead == _token.id:
						token.head_token = _token
					if not "-" in token.id and not "/" in token.id:
						if not "-" in _token.id and not "/" in _token.id:
							if int(token.id) == int(_token.id) - 1:
								token.next_token = _token
							if int(token.id) == int(_token.id) + 1:
								token.previous_token = _token'''

		for token in self.tokens_incompletos:
			self.tokens.append(self.get_head(token))

		x = self.recursivo if isinstance(self.recursivo, int) else 4
		for i in range(x):
			for token in self.tokens:
				token = self.get_head(token)

	def tokens_to_str(self):
		return "\n".join([tok.to_str() for tok in self.tokens])

	def metadados_to_str(self):
		return "\n".join(["# " + x + " = " + self.metadados[x] for x in self.metadados])

	def to_str(self):
		return self.metadados_to_str() + "\n" + self.tokens_to_str()


class Corpus:

	def __init__(self, separator="\n\n", recursivo=0):
		self.len = 0
		self.sentences = {}
		self.separator = separator
		self.sent_list = []
		self.recursivo = recursivo

	def build(self, txt):
		sents = txt.split(self.separator)
		for sentence in sents:
			sent = Sentence(recursivo=self.recursivo)
			sent.build(sentence)
			self.sent_list.append(sent)
			if sent.sent_id:
				self.sentences[sent.sent_id] = sent
			elif sent.id:
				self.sentences[sent.id] = sent
			elif sent.text:
				self.sentences[sent.text] = sent

		self.len = len(self.sentences)

	def to_str(self):
		retorno = list()

		for sentence in self.sentences.values():
			retorno.append(sentence.to_str())
		
		return "\n\n".join(retorno) + '\n\n'

	def load(self, path):
		with open(path, "r") as f:
			self.build(f.read())

	def save(self, path):
		with open(path, "w") as f:
			f.write(self.to_str())
