import estrutura_ud
import interrogar_UD
import sys
import re
import pprint

def validate(conllu, sent_id = None, errorList = "validar_UD.txt"):
    with open(errorList) as f:
        errorListFile = f.read().splitlines()
        errorList = []
        [errorList.append(x) for x in errorListFile]

    errorDictionary = {}
    for error in errorList:
        if error:
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
                sentence.build(sentString)
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
