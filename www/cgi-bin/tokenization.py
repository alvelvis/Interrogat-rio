#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print('Content-type:text/html; charset=utf-8')
print('\n\n')

import cgi, cgitb
cgitb.enable()
import estrutura_ud
import os
import sys
import json
from credenciar import LOGIN

def addToken(conllu, sent_id, option, token_id, conllu_completo="", new_tokens=[], mergeSentencesId="", form=False):

    if form:
        if not os.path.isfile("../cgi-bin/tokenization.json"):
            tokenization = {}
            with open("../cgi-bin/tokenization.json", "w") as f:
                json.dump(tokenization, f)

        with open("../cgi-bin/tokenization.json") as f:
            tokenization = json.load(f)

    corpus = estrutura_ud.Corpus(recursivo=False)
    corpus.load(conllu if not conllu_completo else conllu_completo)

    if token_id == "left":
        token_id = corpus.sentences[sent_id].tokens[0].id
    elif token_id == "right":
        token_id = str(int(corpus.sentences[sent_id].tokens[-1].id)+1)

    if option == "add":
        
        if not new_tokens:
            if not mergeSentencesId:
                novo_token = estrutura_ud.Token()
                novo_token.build("\t".join("_"*10))
                new_tokens.append(novo_token)
            else:
                new_tokens = corpus.sentences[mergeSentencesId].tokens
        else:
            novo_token = estrutura_ud.Token()
            novo_token.build(new_tokens[0])
            new_tokens = [novo_token]

        last_id = ""
        for novo_token in reversed(new_tokens):
            novo_token.id = token_id if not '-' in novo_token.id else str(int(token_id)) + "-" + str(int(token_id)+int(novo_token.id.split("-")[1])-int(novo_token.id.split("-")[0]))
            if mergeSentencesId:
                if not last_id:
                    last_id = corpus.sentences[sent_id].tokens[-1].id
                if token_id == str(int(last_id)+1) and not '-' in novo_token.id:
                    novo_token.dephead = str(int(novo_token.dephead) + int(last_id))
            if not token_id in corpus.sentences[sent_id].map_token_id:
                corpus.sentences[sent_id].tokens.append(novo_token)
                corpus.sentences[sent_id].map_token_id[token_id] = len(corpus.sentences[sent_id].tokens) - 1
            else:
                corpus.sentences[sent_id].tokens.insert(corpus.sentences[sent_id].map_token_id[token_id], novo_token)
            for t, token in enumerate(corpus.sentences[sent_id].tokens):
                if not '-' in novo_token.id:
                    if t > corpus.sentences[sent_id].map_token_id[token_id]:
                        token.id = str(int(token.id)+1) if not '-' in token.id else str(int(token.id.split("-")[0])+1) + "-" + str(int(token.id.split("-")[1])+1)
                        corpus.sentences[sent_id].map_token_id[token.id] = t
            for t, token in enumerate(corpus.sentences[sent_id].tokens):
                if not mergeSentencesId and token.dephead not in ["0", "_"] and corpus.sentences[sent_id].map_token_id[token.dephead] >= corpus.sentences[sent_id].map_token_id[token_id]:
                    token.dephead = str(int(token.dephead)+1)

            if form:
                if not conllu in tokenization:
                    tokenization[conllu] = {}
                if not sent_id in tokenization[conllu]:
                    tokenization[conllu][sent_id] = []
                tokenization[conllu][sent_id].append({'option': option, 'token_id': token_id, 'new_token': [novo_token.to_str()]})

        if mergeSentencesId and token_id != str(int(last_id)+1):
            for t, token in enumerate(corpus.sentences[sent_id].tokens):
                if token.dephead not in ["0", "_"] and t > int(corpus.sentences[sent_id].map_token_id[new_tokens[-1].id]):
                    token.dephead = str(int(token.dephead) + int(new_tokens[-1].id))
                    
        if mergeSentencesId:
            if token_id == corpus.sentences[sent_id].tokens[0].id:
                corpus.sentences[sent_id].metadados['text'] = corpus.sentences[mergeSentencesId].text + corpus.sentences[sent_id].text
            else:
                corpus.sentences[sent_id].metadados['text'] += corpus.sentences[mergeSentencesId].text
            corpus.sentences.pop(mergeSentencesId)

    elif option == "rm":
        for t, token in enumerate(corpus.sentences[sent_id].tokens):
            if t > corpus.sentences[sent_id].map_token_id[token_id]:
                token.id = str(int(token.id)-1) if not '-' in token.id else str(int(token.id.split("-")[0])-1) + "-" + str(int(token.id.split("-")[1])-1)
            if token.dephead not in ["_", "0"]:
                if corpus.sentences[sent_id].map_token_id[token.dephead] > corpus.sentences[sent_id].map_token_id[token_id]:
                    token.dephead = str(int(token.dephead)-1)
        corpus.sentences[sent_id].tokens = [x for t, x in enumerate(corpus.sentences[sent_id].tokens) if t != corpus.sentences[sent_id].map_token_id[token_id]]

        if form:
            if not conllu in tokenization:
                tokenization[conllu] = {}
            if not sent_id in tokenization[conllu]:
                tokenization[conllu][sent_id] = []
            tokenization[conllu][sent_id].append({'option': option, 'token_id': token_id})

    if form:
        with open("../cgi-bin/tokenization.json", "w") as f:
            json.dump(tokenization, f)
        corpus.save(conllu if not conllu_completo else conllu_completo)
    else:
        print(corpus.to_str())

if 'REQUEST_METHOD' in os.environ and os.environ['REQUEST_METHOD'] == 'POST':
    form = cgi.FieldStorage()
    if LOGIN:
        if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
            html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
            print(html)
            exit()

sent_id = form['tokenization_sentid'].value
conllu = form['tokenization_conllu'].value
conllu_completo = "../interrogar-ud/conllu/" + conllu
action = form['action'].value
option = form['addTokenOption'].value if 'addTokenOption' in form else "add"
token_id = form['addTokenId'].value if 'addTokenId' in form else form['mergeSentencesOption'].value
mergeSentencesId = form['mergeSentencesId'].value if "mergeSentencesId" in form else ""

try:
    if action == "addToken":
        addToken(conllu, sent_id, option, token_id, form=form, conllu_completo=conllu_completo)
    elif action == "mergeSentences":
        addToken(conllu, sent_id, option, token_id, mergeSentencesId=mergeSentencesId, form=form, conllu_completo=conllu_completo)

except Exception as e:
    print(e)
    exit()

html = f'<form action="../cgi-bin/inquerito.py" method="POST" id="inquerito">'
for input in form:
    html += f'<input type=hidden name="{input.split("tokenization_")[1] if "tokenization_" in input else input}" value="{form[input].value}">'
html += "</form>"
html += "<script>inquerito.submit();</script>"
print(html)