#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print('Content-type:text/html; charset=utf-8')
print('\n\n')

import cgi, cgitb
cgitb.enable()
import os
import pandas as pd
import datetime
import html as web
from utils import escape_html_except_bold, col_to_idx

inqueritos_folder = "./interrogar-ud/inqueritos"
if not os.path.isdir(inqueritos_folder):
    os.mkdir(inqueritos_folder)

readable_date = lambda x: datetime.datetime.fromtimestamp(x).strftime("%d-%m-%Y %H:%M")

dfs = [pd.read_csv(os.path.join(inqueritos_folder, x), index_col=0) for x in sorted(os.listdir(inqueritos_folder), reverse=True) if x.endswith(".csv")]
df = pd.concat(dfs).reset_index(drop=True)
df.tag.fillna("INQUÉRITO", inplace=True)
df.fillna("", inplace=True)

date = datetime.datetime.now().timestamp()
html = "<title>Relatório de inquéritos</title>"
html += "<h1>Relatório de inquéritos</h1>"
html += "Relatório gerado {}.<hr>".format(readable_date(date))

forms = cgi.FieldStorage()
if 'date' in forms:
    date = float(forms['date'].value)
    rows = df[df.date == date]
    href = rows.href.iloc[0]
    occurrences = rows.occurrences.iloc[0]
    interrogatorio = rows.interrogatorio.iloc[0]
    html += f"<b>{readable_date(date)} ({len(rows)} tokens modificados)</b> [<a href='../cgi-bin/relatorio.py'>Voltar</a>]"
    html += "<br>Página no Interrogatório: "
    html += f"<a href='../{href}'>{web.escape(interrogatorio)} ({occurrences:.0f})</a>" if interrogatorio else "Busca rápida"
    html += "<hr>"
    html += "<pre>"
    for idx in rows.index:
        sent_id = rows["sent_id"][idx]
        text = rows["text"][idx]
        before = rows["before"][idx]
        after = rows["after"][idx]
        head = rows["head"][idx]
        col = rows["col"][idx]
        before_after = ""
        if col in col_to_idx:
            col_before = before.split("\t")[col_to_idx[col]]
            col_after = after.split("\t")[col_to_idx[col]]
            before_after = f"{web.escape(col)}: {web.escape(col_before)} -> {web.escape(col_after)}\n"
            text = escape_html_except_bold(text) + "\n"
            head = f"(head: {web.escape(head)})"
        html += f'{before_after}{web.escape(sent_id)}\n{text}ANTES: {web.escape(before)}\nDEPOIS: {web.escape(after)} {head}\n\n'
    html += "</pre>"
else:
    dates = df.date.unique()
    conllus = df.conllu.unique()
    tags = df.tag.unique()
    
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

    html += "<hr>"
    for date in dates:
        time = readable_date(date)
        rows = df[df.date == date]
        tag = rows.tag.iloc[0]
        conllu = rows.conllu.iloc[0]
        html += f"<a class='inquerito' href='../cgi-bin/relatorio.py?date={date}' date='{time}' conllu='{web.escape(conllu)}' tag='{web.escape(tag)}' style='text-decoration:none; margin:5px; display: block;'>{time} - {web.escape(conllu)} [{web.escape(tag)}] ({len(rows)})</a>"

html += '<script src="../interrogar-ud/jquery-latest.js"></script>'
html += '''
<script>
$('.changeFilter').change(function(){
    $('.inquerito').hide()

    corpusSelection = $('.corpusSelection').val()
    tagSelection = $('.tagSelection').val()

    corpusFilter = 'conllu'
    tagFilter = 'tag'

    if (corpusSelection != "*") {
        corpusFilter = corpusFilter + '="' + corpusSelection + '"'
    }
    if (tagSelection != "*") {
        tagFilter = tagFilter + '="' + tagSelection + '"'
    }

    $('.inquerito[' + corpusFilter + '][' + tagFilter + ']').show()
})
</script>
'''

print(html)