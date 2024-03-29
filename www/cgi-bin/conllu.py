#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html")
print('\n\n')

import os
import cgi,cgitb
cgitb.enable()
import re
from datetime import datetime
from utils import tabela
import html as web

from estrutura_dados import slugify as slugify

form = cgi.FieldStorage()
with open(form['html'].value, 'r') as f:
	html = f.read()
	html = web.unescape(html)
	html = re.split(r'\<pre id=.*?\>', html)
	html = [x.split('</pre>')[0] for x in html[1:]]
	with open('./interrogar-ud/tmp/' + slugify(form['nomeconllu'].value) + '.conllu', 'w') as f:
		f.write(web.unescape("\n\n".join(html).replace('<b>','').replace('</b>','').replace('<font color=' + tabela['yellow'] + '>','').replace('<font color=' + tabela['red'] + '>','').replace('<font color=' + tabela['cyan'] + '>','').replace('<font color=' + tabela['blue'] + '>','').replace('<font color=' + tabela['purple'] + '>','').replace('</font>','') + '\n\n'))

print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body onload="redirect()"><a href="../interrogar-ud/tmp/'+slugify(form['nomeconllu'].value)+'.conllu" download target="_blank" id="download" hidden></a><script>function redirect() { document.getElementById("download").click(); window.history.back(); }</script></body>') #window.location="' + form['html'].value


