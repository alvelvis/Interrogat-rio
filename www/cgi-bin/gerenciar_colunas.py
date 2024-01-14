#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print('Content-type:text/html; charset=utf-8')
print('\n\n')

import cgi, cgitb
cgitb.enable()
import html as web
import estrutura_ud
from estrutura_ud import col_to_idx

forms = cgi.FieldStorage()
conllu = forms['conllu'].value
conllu_file = "./interrogar-ud/conllu/%s" % conllu
conllu_name = conllu.split(".conllu")[0] 

corpus = estrutura_ud.Corpus()
corpus.load(conllu_file)

# FUNÇÕES DE MODIFICAÇÃO
modified = False

if 'new_col' in forms:
    new_col = forms['new_col'].value
    default = forms['default'].value.strip()
    for sentid, sentence in corpus.sentences.items():
        for t, token in enumerate(sentence.tokens):
            if not new_col in token.__dict__:
                token.__dict__[new_col] = default
                modified = True

if 'remove' in forms:
    rm_col = forms['remove'].value
    for sentid, sentence in corpus.sentences.items():
        for t, token in enumerate(sentence.tokens):
            if rm_col in token.__dict__:
                del token.__dict__[rm_col]
                modified = True

if modified:
    corpus.save(conllu_file)
    print("<script>history.pushState({}, null, '?conllu=%s'); window.alert('Modificação realizada com sucesso!')</script>" % conllu)
    corpus = estrutura_ud.Corpus()
    corpus.load(conllu_file)        

# FUNÇÕES DE VISUALIZAÇÃO
cols = {}
cols_per_token = {}
for sentid, sentence in corpus.sentences.items():
    for t, token in enumerate(sentence.tokens):
        if '-' in token.id:
            continue
        n_cols = 0
        for col in token.__dict__:
            if col in col_to_idx or (col.startswith("col") and col != "color"):
                value = token.__dict__[col]
                if not col in cols:
                    cols[col] = {}
                if not value in cols[col]:
                    cols[col][value] = 0
                cols[col][value] += 1
                n_cols += 1
        if not n_cols in cols_per_token:
            cols_per_token[n_cols] = 0
        cols_per_token[n_cols] += 1

html = "<head>"
html += "<title>%s | Gerenciamento de colunas</title>" % conllu_name
html += "<style>td, table, th { border: none; border-left: none; border-right: none; }</style>"
html += "</head>"
html += "<h1>%s</h1>" % conllu_name
html += "Colunas (%s): " % len(cols) + " | ".join(['''<a style='text-decoration:none; color:blue;' href='#' onclick='$(".col").hide(); $(".col[col={0}]").show();' col="{0}">{0}</a>'''.format(x) for x in cols.keys()])
html += "<hr>"
html += "O corpus tem " + ", ".join(["{:,} token{} com {} colunas".format(cols_per_token[n], "s" if cols_per_token[n]>1 else "", n) for n in cols_per_token]) + "."
html += "<hr>"
html += "<b>Adicionar coluna</b> - Valor padrão: <input type=text style='text-align:center' value='_' id='new_col_default'> <input type='button' id='addCol' onclick='add_col({0})' value='col{0}'>".format(len(cols)+1, conllu)
html += "<hr>"
html += "Remover coluna: " + ", ".join(['''<a style='text-decoration:none; color:blue;' href='#' onclick='remove_col("{0}")'>{0}</a>'''.format(x) for x in cols if x not in col_to_idx])
html += "<hr>"

for col in cols:
    html += "<table style='display:none; margin:20px;' class='col' col='%s'>" % col
    html += "<tr><th>%s (%s)</th><th>freq. (%s)</th>" % (col, len(cols[col]), sum(cols[col].values()))
    for val in sorted(cols[col], key=lambda x: cols[col][x], reverse=True):
        html += "<tr><td>%s</td><td>%s</td></tr>" % (val, cols[col][val])
    html += "</table>\n"

html += '<script src="../interrogar-ud/jquery-latest.js"></script>'
html += '''<script>
function add_col(new_col) {{
    addCol.value = "AGUARDE..."
    addCol.disabled = true
    value = $('#new_col_default').val()
    if (value.trim().length>0) {{
        window.location.href = "?conllu={conllu}&default=" + encodeURI(value) + "&new_col=col" + encodeURI(new_col)
    }}
}}
function remove_col(col) {{ 
    if (window.confirm('A coluna "' + col + '" tem ' + ($(".col[col=" + col + "]").find("tr").length-1).toString() + ' valores diferentes. Tem certeza de que deseja removê-la do corpus "{conllu}"?')) {{ 
        window.location.href = "?conllu={conllu}&remove=" + col
    }} 
}}
</script>'''.format(conllu=web.escape(conllu))
print(html)