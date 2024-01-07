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
from estrutura_ud import col_to_idx
from utils import escape_html_except_bold, fastsearch
forms = cgi.FieldStorage()

inqueritos_folder = "./interrogar-ud/inqueritos"
if not os.path.isdir(inqueritos_folder):
    os.mkdir(inqueritos_folder)

readable_date = lambda x: datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M")

if not 'id' in forms:
    dfs = [pd.read_csv(os.path.join(inqueritos_folder, x), index_col=0) for x in sorted(os.listdir(inqueritos_folder), reverse=True) if x.endswith(".csv")]
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
if 'id' in forms:
    html += "[<a href='../cgi-bin/relatorio.py'>Todos os relatórios</a>]<br><br>"
html += "Relatório gerado {}.".format(readable_date(date))
html += "<hr>"

if 'id' in forms:
    _id = forms['id'].value
    rows = df[df._id == _id]
    date = rows.date.iloc[0]
    href = rows.href.iloc[0]
    tag = rows.tag.iloc[0]
    conllu = rows.conllu.iloc[0]
    interrogatorio = rows.interrogatorio.iloc[0]
    html += f"<b>{readable_date(date)} ({len(rows)} tokens modificados)</b>"
    html += "<br>Nome da correção: %s" % tag
    html += "<br>Busca: "
    html += f"<a target='_blank' href='../{href}'>{web.escape(interrogatorio)}</a>" if interrogatorio not in fastsearch else web.escape(interrogatorio)
    html += "<br>Corpus: <a href='../interrogar-ud/conllu/{ud}.conllu'>{ud}.conllu</a>".format(ud=web.escape(conllu))
    html += "<hr>"
    html += "<pre>"
    for idx in rows.index:
        sent_id = str(rows["sent_id"][idx])
        text = rows["text"][idx]
        col = rows["col"][idx] if 'col' in rows.columns else None
        before = rows["before"][idx]
        after = rows["after"][idx]
        sys.stderr.write(str(int(col.split("col")[1])-1))
        if col and (col in col_to_idx or col.startswith("col")):
            before = "\t".join([x if col_to_idx.get(col, int(col.split("col")[1])-1) != i else "<b>%s</b>" % x for i, x in enumerate(before.split("\t"))])
            after = "\t".join([x if col_to_idx.get(col, int(col.split("col")[1])-1) != i else "<b>%s</b>" % x for i, x in enumerate(after.split("\t"))])
        head = rows["head"][idx]
        before_after = ""
        if text:
            text = escape_html_except_bold(text) + "\n"
        if head:
            head = f"(head: {web.escape(head)})"
        html += f'{web.escape(sent_id)}\n{text}ANTES: {escape_html_except_bold(before)}\nDEPOIS: {escape_html_except_bold(after)} {head}\n\n'
    html += "</pre>"
else:
    _ids = df._id.unique()
    dates = df.date.unique()
    conllus = df.conllu.unique()
    tags = df.tag.unique()
    interrogatorios = df.interrogatorio.unique()
    
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