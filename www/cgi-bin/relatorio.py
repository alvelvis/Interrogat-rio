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
forms = cgi.FieldStorage()

inqueritos_folder = "./interrogar-ud/inqueritos"
if not os.path.isdir(inqueritos_folder):
    os.mkdir(inqueritos_folder)

readable_date = lambda x: datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M")

dfs = [pd.read_csv(os.path.join(inqueritos_folder, x), index_col=0) for x in sorted(os.listdir(inqueritos_folder), reverse=True) if x.endswith(".csv")]
if not dfs:
    print("Nenhum inquérito foi finalizado ainda.")
    exit()
df = pd.concat(dfs).reset_index(drop=True)
df.tag.fillna("INQUÉRITO", inplace=True)
df.fillna("", inplace=True)

date = datetime.datetime.now().timestamp()
html = "<title>Relatório de inquéritos</title>"
html += "<h1>Relatório de inquéritos</h1>"
if 'date' in forms:
    html += "[<a href='../cgi-bin/relatorio.py'>Todos os relatórios</a>]<br><br>"
html += "Relatório gerado {}.".format(readable_date(date))
html += "<hr>"

if 'date' in forms:
    date = float(forms['date'].value)
    rows = df[df.date == date]
    href = rows.href.iloc[0]
    tag = rows.tag.iloc[0]
    conllu = rows.conllu.iloc[0]
    occurrences = rows.occurrences.iloc[0]
    interrogatorio = rows.interrogatorio.iloc[0]
    html += f"<b>{readable_date(date)} ({len(rows)} tokens modificados)</b>"
    html += "<br>Nome da correção: %s" % tag
    html += "<br>Busca inicial: "
    html += f"<a target='_blank' href='../{href}'>{web.escape(interrogatorio)} ({occurrences:.0f})</a>" if interrogatorio else "Busca rápida"
    html += "<br>Corpus: <a href='../interrogar-ud/conllu/{ud}.conllu'>{ud}.conllu</a>".format(ud=web.escape(conllu))
    html += "<hr>"
    html += "<pre>"
    for idx in rows.index:
        sent_id = str(rows["sent_id"][idx])
        text = rows["text"][idx]
        col = rows["col"][idx]
        before = rows["before"][idx]
        after = rows["after"][idx]
        if col in col_to_idx:
            before = "\t".join([x if col_to_idx[col] != i else "<b>%s</b>" % x for i, x in enumerate(before.split("\t"))])
            after = "\t".join([x if col_to_idx[col] != i else "<b>%s</b>" % x for i, x in enumerate(after.split("\t"))])
        head = rows["head"][idx]
        before_after = ""
        if text:
            text = escape_html_except_bold(text) + "\n"
        if head:
            head = f"(head: {web.escape(head)})"
        html += f'{web.escape(sent_id)}\n{text}ANTES: {escape_html_except_bold(before)}\nDEPOIS: {escape_html_except_bold(after)} {head}\n\n'
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