#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print('Content-type:text/html; charset=utf-8')
print('\n\n')

import cgi, cgitb
cgitb.enable()
import os
import pandas as pd
import datetime
import sys
import html as web
import uuid
from utils import build_modifications_html, readable_date
forms = cgi.FieldStorage()

inqueritos_folder = "./interrogar-ud/inqueritos"
if not os.path.isdir(inqueritos_folder):
    os.mkdir(inqueritos_folder)

if not 'id' in forms:
    dfs = [pd.read_csv(os.path.join(inqueritos_folder, x), index_col=0, dtype=str) for x in sorted(os.listdir(inqueritos_folder), reverse=True) if x.endswith(".csv")]
    if not dfs:
        print("Nenhum inquérito foi finalizado ainda.")
        exit()

    # Backwards compatibility
    if ' ' in "".join(os.listdir(inqueritos_folder)):
        sys.stderr.write("===== CLEANING %s" % inqueritos_folder)
        for df in dfs:
            if not '_id' in df.columns:
                _id = str(uuid.uuid4())
                df['_id'] = _id
                df.to_csv(os.path.join(inqueritos_folder, "%s.csv" % _id))
        for filename in os.listdir(inqueritos_folder):
            if ' ' in filename:
                os.remove(os.path.join(inqueritos_folder, filename))
    
    df = pd.concat(dfs)
    df.sort_values('date', ascending=False, inplace=True)
else:
    df = pd.read_csv(os.path.join(inqueritos_folder, "%s.csv" % forms['id'].value))

df.tag.fillna("INQUÉRITO", inplace=True)
df.interrogatorio.fillna("Busca rápida", inplace=True)
df.fillna("", inplace=True)

date = datetime.datetime.now().timestamp()
html = "<title>Relatório de inquéritos</title>"
html += "<h1>Relatório de inquéritos</h1>"
html += "Relatório gerado {}.".format(readable_date(date))
html += "<hr>"

if 'id' in forms:
    html += " [<a href='../cgi-bin/relatorio.py' style='color:blue'>Todos os relatórios</a>]"
    html += " [<a href='../cgi-bin/relatorio.py?rules=%s' style='color:blue'>Transformar em regras</a>]" % forms['id'].value
    html += "<br><br>"
    html += build_modifications_html(df, forms['id'].value)
elif 'rules' in forms:
    _ids = forms['rules'].value.split(",")
    modifications = []
    rows = df[df._id.isin(_ids)].reset_index()
    rule = ""
    full_query = rows['full_query'].iloc[0] if 'full_query' in df.columns and len(_ids) == 1 else ""
    if full_query and isinstance(full_query, str):
        rule = "if %s:\n" % full_query
    tab = "\t" if rule else ""
    for i, idx in enumerate(rows.index):
        sent_id = rows['sent_id'][idx]
        col = rows['col'][idx]
        value = rows['value'][idx] if 'value' in rows.columns else ""
        token_id = rows['token_id'][idx] if 'token_id' in rows.columns else ""
        if isinstance(value, str) and value and isinstance(token_id, str) and token_id:
            modifications.append(f'{tab}if sentence.sent_id == "{sent_id}" and token.id == "{token_id}":\n{tab}\ttoken.{col} = "{value}"')
    print("<pre>" + web.escape(rule + "\n".join(modifications)) + "</pre>")
    exit()
elif 'download' in forms:
    tag = forms['download'].value
    interrogatorio = forms['interrogatorio'].value
    conllu = forms['conllu'].value
    if conllu != "*":
        df = df[df.conllu == conllu]
    if interrogatorio != "*":
        df = df[df.interrogatorio == interrogatorio]
    df = df[df.tag == tag]
    _ids = df._id.unique()
    html += " [<a href='../cgi-bin/relatorio.py' style='color:blue'>Todos os relatórios</a>]"
    html += " [<a href='../cgi-bin/relatorio.py?rules=%s' style='color:blue'>Transformar em regras</a>]" % ",".join(_ids)
    html += "<br><br>"
    html += "Soma de modificações: %s<hr><hr>" % len(df)
    for _id in _ids:
        html += build_modifications_html(df, _id)
        html += "<hr><hr>"
else:
    _ids = df._id.unique()
    dates = df.date.unique()
    conllus = df.conllu.unique()
    tags = df.tag.unique()
    interrogatorios = df.interrogatorio.unique()
    html += '''[<a href='#' onclick='download_inqueritos_manuais();'>Juntar todos os inquéritos dessa página</a>]<br><br>'''
    html += "<select class='changeFilter corpusSelection'>"
    html += f'<option value="*">Todos os corpora ({len(conllus)} corpora)</option>'
    for conllu in conllus:
        html += f"<option value='{web.escape(conllu)}'>{web.escape(conllu)} ({len(df[df.conllu == conllu])} modificações)</option>"
    html += "</select>"

    html += "<select class='changeFilter tagSelection'>"
    html += f'<option value="*">Todas as correções ({len(tags)} tipos)</option>'
    for tag in tags:
        html += f"<option value='{web.escape(tag)}'>{web.escape(tag)} ({len(df[df.tag == tag])} modificações)</option>"
    html += "</select>"

    html += "<select class='changeFilter interrogatorioSelection'>"
    html += f'<option value="*">Todas as buscas ({len(interrogatorios)} buscas)</option>'
    for interrogatorio in interrogatorios:
        html += f"<option value='{web.escape(interrogatorio)}'>{web.escape(interrogatorio)} ({len(df[df.interrogatorio == interrogatorio])} modificações)</option>"
    html += "</select>"

    html += "<hr>"
    html += "Total de modificações: %s<hr>" % len(df)

    for _id in _ids:
        rows = df[df._id == _id]
        date = rows.date.iloc[0]
        interrogatorio = rows.interrogatorio.iloc[0]
        time = readable_date(date)
        tag = rows.tag.iloc[0]
        conllu = rows.conllu.iloc[0]
        html += f"<a class='inquerito' href='../cgi-bin/relatorio.py?id={_id}' date='{time}' conllu='{web.escape(conllu)}' tag='{web.escape(tag)}' interrogatorio='{web.escape(interrogatorio)}' style='text-decoration:none; margin:5px; display: block;'>{time} - {web.escape(conllu)} - {web.escape(tag)} - {web.escape(interrogatorio)} - {len(rows)} modificações</a>"

html += '<hr><br><br>'
html += '<script src="../interrogar-ud/jquery-latest.js"></script>'
html += '''
<script>
function download_inqueritos_manuais() {
    //$('.tagSelection').val('INQUÉRITO')
    //$('.tagSelection').change()
    window.location.href = "../cgi-bin/relatorio.py?download=" + encodeURIComponent($('.tagSelection').val()) + "&interrogatorio=" + encodeURIComponent($('.interrogatorioSelection').val()) + "&conllu=" + encodeURIComponent($('.corpusSelection').val())
}
$('.changeFilter').change(function(){
    $('.inquerito').hide()

    corpusSelection = $('.corpusSelection').val()
    corpusFilter = 'conllu'
    if (corpusSelection != "*") {
        corpusFilter = corpusFilter + '="' + corpusSelection + '"'
    }

    tagSelection = $('.tagSelection').val()
    tagFilter = 'tag'
    if (tagSelection != "*") {
        tagFilter = tagFilter + '="' + tagSelection + '"'
    }

    interrogatorioSelection = $('.interrogatorioSelection').val()
    interrogatorioFilter = 'interrogatorio'
    if (interrogatorioSelection != "*") {
        interrogatorioFilter = interrogatorioFilter + '="' + interrogatorioSelection + '"'
    }

    $('.inquerito[' + corpusFilter + '][' + tagFilter + '][' + interrogatorioFilter + ']').show()
})
</script>
'''

print(html)
