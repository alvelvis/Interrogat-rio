#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import cgi, cgitb
cgitb.enable()
import estrutura_ud
import os
import sys
import json
from credenciar import LOGIN

def splitSentence(conllu, sent_id, token_id, conllu_completo="", form=False):

    if form:
        if not os.path.isfile("../cgi-bin/tokenization.json"):
            tokenization = {}
            with open("../cgi-bin/tokenization.json", "w") as f:
                json.dump(tokenization, f)

        with open("../cgi-bin/tokenization.json") as f:
            tokenization = json.load(f)

    corpus = estrutura_ud.Corpus(recursivo=False)
    corpus.load(conllu if not conllu_completo else conllu_completo)

    new_sentence = estrutura_ud.Sentence(recursivo=True)
    new_sentence.build(corpus.sentences[sent_id].to_str())

    sent_id_file = sent_id.rsplit("-", 1)[0] if '-' in sent_id else ""
    all_sentid = [int(x.rsplit("-", 1)[1]) if '-' in x else int(x) for x in corpus.sentences if x.startswith(sent_id_file)]
    new_sentence.sent_id = f"{sent_id_file}{'-' if sent_id_file else ''}{max(all_sentid) + 1}"
    new_sentence.metadados['sent_id'] = f"{sent_id_file}{'-' if sent_id_file else ''}{max(all_sentid) + 1}"

    new_token = False
    new_sentence_tokens = []
    old_sentence_tokens = []
    removed_tokens = 0
    for token in corpus.sentences[sent_id].tokens:
        if new_token:
            new_sentence_tokens.append(token)
        else:
            old_sentence_tokens.append(token)
        if not '-' in token.id and not new_token:
            removed_tokens += 1
        if token.id == token_id:
            new_token = True
        
    new_sentence.tokens = new_sentence_tokens
    corpus.sentences[sent_id].tokens = old_sentence_tokens
    corpus.sentences[new_sentence.sent_id] = new_sentence
    corpus.sentences[new_sentence.sent_id].refresh_map_token_id()

    for t, token in enumerate(corpus.sentences[new_sentence.sent_id].tokens):
        token.id = str(int(token.id)-removed_tokens) if not '-' in token.id else str(int(token.id.split("-")[0])-removed_tokens) + "-" + str(int(token.id.split("-")[1])-removed_tokens)
        if token.dephead not in ["_", "0"]:
            token.dephead = str(int(token.dephead)-removed_tokens)
            if int(token.dephead) < 0:
                token.dephead = "0"

    if form:
        with open("../cgi-bin/tokenization.json", "w") as f:
            json.dump(tokenization, f)
        corpus.save(conllu + "_tokenization" if not conllu_completo else conllu_completo + "_tokenization")
        os.remove(conllu if not conllu_completo else conllu_completo)
        os.rename(conllu + "_tokenization" if not conllu_completo else conllu_completo + "_tokenization", conllu if not conllu_completo else conllu_completo)
        return new_sentence.sent_id
    else:
        print(corpus.to_str())

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

    if option in ["add", "addContraction"]:
        
        if not new_tokens:
            if not mergeSentencesId:
                novo_token = estrutura_ud.Token()
                novo_token.build("_\t_\t_\t_\t_\t_\t0\t_\t_\t_")
                new_tokens.append(novo_token)
            else:
                new_tokens = corpus.sentences[mergeSentencesId].tokens
        else:
            novo_token = estrutura_ud.Token()
            novo_token.build(new_tokens[0])
            new_tokens = [novo_token]

        last_id = ""
        for novo_token in reversed(new_tokens):
            if option == "add":
                novo_token.id = token_id if not '-' in novo_token.id else str(int(token_id)) + "-" + str(int(token_id)+int(novo_token.id.split("-")[1])-int(novo_token.id.split("-")[0]))
            elif option == "addContraction":
                novo_token.id = token_id + "-" + token_id
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
            if option == "add":
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
                corpus.sentences[sent_id].metadados['text'] = corpus.sentences[mergeSentencesId].text + ' ' + corpus.sentences[sent_id].text
            else:
                corpus.sentences[sent_id].metadados['text'] += ' ' + corpus.sentences[mergeSentencesId].text
            corpus.sentences.pop(mergeSentencesId)

    elif option in ["rm"]:
        if not '-' in token_id:
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
        corpus.save(conllu + "_tokenization" if not conllu_completo else conllu_completo + "_tokenization")
        os.remove(conllu if not conllu_completo else conllu_completo)
        os.rename(conllu + "_tokenization" if not conllu_completo else conllu_completo + "_tokenization", conllu if not conllu_completo else conllu_completo)
    else:
        print(corpus.to_str())

form = ""
if 'REQUEST_METHOD' in os.environ and os.environ['REQUEST_METHOD'] == 'POST':
    form = cgi.FieldStorage()
    if LOGIN:
        if (not 'HTTP_COOKIE' in os.environ) or ('HTTP_COOKIE' in os.environ and not 'conectado' in os.environ['HTTP_COOKIE']):
            html = '<script>window.location = "../interrogar-ud/autenticar.html"</script>'
            print(html)
            exit()

if form:
    print('Content-type:text/html; charset=utf-8')
    print('\n\n')

    sent_id = form['tokenization_sentid'].value
    conllu = form['tokenization_conllu'].value
    conllu_completo = "../interrogar-ud/conllu/" + conllu
    action = form['action'].value
    option = form['addTokenOption'].value if 'addTokenOption' in form else "add"
    if 'addTokenId' in form:
        token_id = form['addTokenId'].value 
    elif 'mergeSentencesOption' in form:
        token_id = form['mergeSentencesOption'].value
    elif 'splitSentenceTokenId' in form:
        token_id = form['splitSentenceTokenId'].value
    token_id = token_id.replace(" ", "")

    mergeSentencesId = form['mergeSentencesId'].value if "mergeSentencesId" in form else ""

    new_sent_id = ""
    if action == "addToken":
        token_split = token_id.split(",")
        list_tokens = [x for x in token_split if '-' in x] + sorted([int(x) for x in token_split if x.isnumeric()], reverse=True) + [x for x in token_split if not x.isnumeric() and not '-' in x]
        for token in list_tokens:
            if token:
                addToken(conllu, sent_id, option, str(token), new_tokens=[], mergeSentencesId="", form=form, conllu_completo=conllu_completo)
    elif action == "mergeSentences":
        sent_split = [x.strip() for x in mergeSentencesId.split(",")]
        for sent in sent_split:
            addToken(conllu, sent_id, option, token_id, mergeSentencesId=sent, form=form, conllu_completo=conllu_completo)
    elif action == "splitSentence":
        new_sent_id = splitSentence(conllu, sent_id, token_id, form=form, conllu_completo=conllu_completo)

    html = f'<form action="../cgi-bin/inquerito.py" method="POST" id="inquerito"><input type=hidden name="tokenizado" value="{new_sent_id if new_sent_id else "True"}">'
    for input in form:
        html += f'<input type=hidden name="{input.split("tokenization_")[1] if "tokenization_" in input else input}" value="{form[input].value}">'
    html += "</form>"
    html += "<script>inquerito.submit();</script>"
    print(html)
