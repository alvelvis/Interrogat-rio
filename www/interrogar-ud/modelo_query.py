import estrutura_ud
import interrogar_UD
import re
import cgi
import html as web
from functions import tabela as tabelaf

def getResultadosBusca():
    corpus = estrutura_ud.Corpus(recursivo=True)
    corpus.load("<!--corpus-->")

    resultadosBusca = {'output': [], 'casos': 0, 'parameters': ""}

    returned_tokens = {}
    for sent_id, sentence in corpus.sentences.items():
        bold_tokens = []
        <!--pesquisa-->

        if bold_tokens:
            returned_tokens[sent_id] = list(set(bold_tokens))
        
        if 'corresponde' in sentence.metadados:
            del sentence.metadados['corresponde'] # retrocompatibility
    
    for sent_id in returned_tokens:
        returned_tokens[sent_id] = ",".join([x.id for x in returned_tokens[sent_id]])
    parameters = 'tokens=' + "|".join(["%s:%s" % (x, returned_tokens[x]) for x in returned_tokens])
    resultadosBusca = interrogar_UD.main(corpus, 5, parameters, fastSearch=True)
    resultadosBusca['scriptParams'] = parameters
    return resultadosBusca
