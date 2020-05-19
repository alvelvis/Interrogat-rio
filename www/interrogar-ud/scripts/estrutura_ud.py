import sys, re

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

class Token:
	
	def __init__(self, separator='\t'):
		self.id = "0"
		self.word = "_"
		self.lemma = "_"
		self.upos = "_"
		self.xpos = "_"
		self.feats = "_"
		self.dephead = "0"
		self.deprel = "_"
		self.deps = "_"
		self.sema = "_"
		self.misc = "_"
		self.children = []
		self.separator = separator
		self.col = dict()
		#self.sent_id = sent_id
		#self.text = text
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
		self.col["sema"] = self.deps
		self.col["misc"] = self.misc
		#self.col["text"] = self.text

	def to_str(self):
		return self.separator.join([self.id, self.word, self.lemma, self.upos, self.xpos, self.feats, self.dephead, self.deprel, self.deps, self.misc])


class Sentence:

	def __init__(self, separator="\n", recursivo=True):
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
		self.map_token_id = {}

	def build(self, txt):
		if '# text =' in txt:
			self.text = txt.split('# text =')[1].split('\n')[0].strip()
			self.metadados['text'] = self.text
		if '# sent_id =' in txt:
			self.sent_id = txt.split('# sent_id =')[1].split('\n')[0].strip()
			self.metadados['sent_id'] = self.sent_id
		if '# source =' in txt:
			self.source = txt.split('# source =')[1].split('\n')[0].strip()
			self.metadados['source'] = self.source
		if '# id =' in txt:
			self.id = txt.split('# id =')[1].split('\n')[0].strip()
			self.metadados["id"] = self.id
		
		n_token = 0
		for linha in txt.split(self.separator):
			try:
				if linha and linha.startswith('# ') and " = " in linha:
					identificador = linha.split("#", 1)[1].split('=', 1)[0].strip()
					if identificador not in ["text", "sent_id", "source", "id"]:
						valor = linha.split('=', 1)[1].strip()
						self.metadados[identificador] = valor
				if not linha.startswith("# ") and "\t" in linha:
					tok = Token()
					tok.build(linha)
					tok.head_token = self.default_token
					tok.next_token = self.default_token
					tok.previous_token = self.default_token
					self.map_token_id[re.sub(r"<.*?>", "", tok.id) if '<' in tok.id else tok.id] = n_token
					self.tokens.append(tok)
					n_token += 1
			except Exception as e:
				sys.stderr.write(str(e + "\n"))
				sys.stderr.write(str(linha + "\n"))
				sys.exit()

		if self.recursivo != False:
			for token in self.tokens:
				if not '-' in token.id:
					token_dephead = token.dephead if not '<' in token.dephead else re.sub(r"<.*?>", "", token.dephead)
					token_id = token.id if not '<' in token.id else re.sub(r"<.*?>", "", token.id)
					token.head_token = self.tokens[self.map_token_id[token_dephead]] if token_dephead in self.map_token_id else self.default_token
					token.next_token = self.tokens[self.map_token_id[str(int(token_id)+1)]] if str(int(token_id)+1) in self.map_token_id else self.default_token
					token.previous_token = self.tokens[self.map_token_id[str(int(token_id)-1)]] if str(int(token_id)-1) in self.map_token_id else self.default_token
					#token.head_token = self.tokens[self.map_token_id[token.dephead]] if token.dephead in self.map_token_id else self.default_token
					#token.next_token = self.tokens[self.map_token_id[str(int(token.id)+1)]] if str(int(token.id)+1) in self.map_token_id else self.default_token
					#token.previous_token = self.tokens[self.map_token_id[str(int(token.id)-1)]] if str(int(token.id)-1) in self.map_token_id else self.default_token

	def refresh_map_token_id(self):
		self.map_token_id = {x.id: y for y, x in enumerate(self.tokens)}

	def tokens_to_str(self):
		return "\n".join([tok.to_str() for tok in self.tokens])

	def metadados_to_str(self):
		return "\n".join(["# " + x + " = " + self.metadados[x] for x in self.metadados])

	def to_str(self):
		return self.metadados_to_str() + "\n" + self.tokens_to_str()


class Corpus:

	def __init__(self, separator="\n\n", recursivo=True, sent_id=None, thread=False, encoding="utf-8", keywords=[], any_of_keywords=[]):
		self.len = 0
		self.sentences = {}
		self.sentences_not_built = {}
		self.separator = separator
		self.recursivo = recursivo
		self.sent_id = sent_id
		self.encoding = encoding
		self.pre = ""
		self.pos = ""
		self.thread = thread
		self.keywords = keywords
		self.any_of_keywords = any_of_keywords

	def build(self, txt):
		if self.sent_id:
			old_txt = txt
			txt = re.search(r"(\n\n|^).*?# sent_id = " + self.sent_id + r"\n.*?(\n\n|$)", txt, flags=re.DOTALL)[0].strip()
			if '\n\n' in txt: txt = txt.rsplit("\n\n", 1)[1]
			self.pre = old_txt.split(txt)[0].strip()
			self.pos = old_txt.split(txt)[1].strip()
			txt = txt.split(self.separator)
		if isinstance(txt, str):
			txt = txt.split(self.separator)
		for sentence in txt:
			if sentence:
				sent = Sentence(recursivo=self.recursivo)
				sent.build(sentence)
				if sent.sent_id:
					self.sentences[sent.sent_id] = sent
				elif sent.id:
					self.sentences[sent.id] = sent
				elif sent.text:
					self.sentences[sent.text] = sent


	def to_str(self):
		self.sentences_not_built.update(self.sentences)
		retorno = [x.to_str() if isinstance(x, Sentence) else x for x in self.sentences_not_built.values()]
		return "\n\n".join(retorno) + '\n\n'

	def load(self, path):
		sentence = ""
		with open(path, "r", encoding=self.encoding) as f:
			if self.keywords and all(x in "ADJ|ADP|ADV|AUX|CCONJ|DET|INTJ|NOUN|NUM|PART|PRON|PROPN|PUNCT|SCONJ|SYM|VERB|X|acl|advcl|advmod|amod|appos|aux|case|cc|ccomp|clf|compound|conj|cop|csubj|dep|det|discourse|dislocated|expl|fixed|flat|goeswith|iobj|list|mark|nmod|nsubj|nummod|obj|obl|orphan|parataxis|punct|reparandum|root|vocative|xcomp".split("|") for x in self.keywords):
				sys.stderr.write("\nthreading active\n")
				
				import threading
				import multiprocessing
				chunks = chunkIt(f.read().split(self.separator), multiprocessing.cpu_count())

				threads = []
				for i in range(multiprocessing.cpu_count()):
					p = threading.Thread(target=self.build, args=(chunks[i],))
					threads.append(p)
					p.start()
				
				for thread in threads:
					thread.join()

			elif not self.sent_id:
				for line in f:
					if line.strip():
						sentence += line
					else:
						if self.keywords:
							if (self.any_of_keywords and any(y in sentence for y in self.any_of_keywords)) or (all(re.search(x, sentence) for x in self.keywords)):
								self.build([sentence])
							elif '# sent_id = ' in sentence:
								self.sentences_not_built[sentence.split("# sent_id = ")[1].split("\n")[0]] = sentence.strip()
						else:
							if not self.any_of_keywords or any(re.search(y, sentence) for y in self.any_of_keywords):
								self.build([sentence])
						sentence = ""
			else:
				self.build(f.read())

	def save(self, path):
		final = self.to_str() if not self.sent_id else (self.pre + "\n\n" + self.to_str() + self.pos).strip() + "\n\n"
		with open(path, "w") as f:
			f.write(final)
