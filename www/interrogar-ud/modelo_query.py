import estrutura_ud
import re
import cgi
import html as web
from functions import tabela as tabelaf

def bold_tokenize(bold_tokens, sentence):
    retorno = sentence.to_str()
    for token in bold_tokens:
        retorno = retorno.replace(token.to_str(), "<b>" + token.to_str() + "</b>").replace(sentence.text, re.sub(r"\b" + re.escape(token.word) + r"\b", "<b>" + token.word + "</b>", sentence.text))
    return retorno

def getResultadosBusca():
    corpus = estrutura_ud.Corpus(recursivo=True)
    corpus.load("<!--corpus-->")

    resultadosBusca = {'output': [], 'casos': 0, 'parameters': ""}

    for sentence in corpus.sentences.values():
        bold_tokens = []
        <!--pesquisa-->

        if 'corresponde' in sentence.metadados and sentence.metadados['corresponde']:
            sentence.metadados['corresponde'] = ""
            resultadosBusca['output'].append({'resultado': bold_tokenize(bold_tokens, sentence)})

    return resultadosBusca
