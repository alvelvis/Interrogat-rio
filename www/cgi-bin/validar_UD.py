import estrutura_ud
import interrogar_UD
import sys
import re
import pprint
from functions import fromInterrogarToHtml

def validate(conllu, sent_id = None, errorList = "validar_UD.txt", noMissingToken=False):

    errorDictionary = {}

    if isinstance(conllu, str):
        corpus = estrutura_ud.Corpus(recursivo=True, sent_id=sent_id)
        corpus.load(conllu)
    else:
        corpus = conllu

    for sentence in corpus.sentences.values():
        if not sentence.text.endswith(sentence.tokens[-1].word):
            if not '1 - Sentença não termina com o último token' in errorDictionary:
                errorDictionary['1 - Sentença não termina com o último token'] = []
            errorDictionary['1 - Sentença não termina com o último token'].append({
                "sentence": "",
                "sent_id": sentence.sent_id,
            })

        temRoot = False
        tem2Root = False
        for token in sentence.tokens:
            if token.deprel == "root" and not temRoot:
                temRoot=True
            elif token.deprel == "root" and temRoot:
                tem2Root=True
        if tem2Root:
            if not '1 - Tem 2 root' in errorDictionary:
                errorDictionary['1 - Tem 2 root'] = []
            errorDictionary['1 - Tem 2 root'].append({
                "sentence": "",
                "sent_id": sentence.sent_id,
            })
        if not temRoot:
            if not '1 - Não tem root' in errorDictionary:
                errorDictionary['1 - Não tem root'] = []
            errorDictionary['1 - Não tem root'].append({
                "sentence": "",
                "sent_id": sentence.sent_id,
            })

    if not noMissingToken:
        missingToken = re.findall(r"\n\n(?!#|$).*", corpus.to_str())
        if missingToken:
            if not '1 - Há tokens faltando no corpus' in errorDictionary:
                errorDictionary['1 - Há tokens faltando no corpus'] = []
            for missing in missingToken:
                errorDictionary['1 - Há tokens faltando no corpus'].append({
                    "sentence": "",
                    "sent_id": "<pre>" + missing + "</pre>",
                })

    with open(errorList) as f:
        errorListFile = f.read().splitlines()
        errorList = []
        [errorList.append(x) for x in errorListFile]

    for error in errorList:
        if error and error[0] != "#":
            if "erro: " in error:
                comment = error.split("erro: ")[1]
                comment = comment.strip()
                coluna = error.split("|", 1)[0] if "|" in error.split("erro: ")[0] else ""
                continue

            parameters = error.strip()
            for sentString in interrogar_UD.main(conllu, 5, parameters, 0, sent_id)['output']:
                if not comment in errorDictionary:
                    errorDictionary[comment] = []
                sentence = estrutura_ud.Sentence(recursivo=True)
                sentence.build(fromInterrogarToHtml(sentString['resultado']))
                tokenT = 0
                for t, token in enumerate(sentence.tokens):
                    if "<b>" in token.to_str():
                        tokenT = t
                        break

                errorDictionary[comment].append({
                    "t": tokenT,
                    "sentence": sentence,
                    "attribute": coluna,
                })


    return errorDictionary

if __name__ == "__main__":
    pprint.pprint(validate(
        conllu=sys.argv[1],
        sent_id=sys.argv[2] if len(sys.argv) > 2 else None, 
        errorList=sys.argv[3] if len(sys.argv) > 3 else "validar_UD.txt"
    ))
