#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html")
print('\n\n')

import os
import cgi,cgitb
cgitb.enable()
from estrutura_dados import slugify as slugify

form = cgi.FieldStorage()
link = './interrogar-ud/resultados/' + form["query"].value + '.html'

print('''<head>
           <meta http-equiv="content-type" content="text/html; charset=UTF-8">
         </head>''')

if os.path.isfile(link):
	import shutil
	os.rename(link, './interrogar-ud/tmp/' + form['query'].value + '.html')
	if os.path.isdir('./interrogar-ud/resultados/' + form["query"].value):
		os.rename('./interrogar-ud/resultados/' + form["query"].value, './interrogar-ud/tmp/' + form["query"].value)
	with open('./interrogar-ud/queries.txt', 'r', encoding="utf-8") as f:
		queries = f.read().splitlines()
	for i, query in enumerate(queries):
		if slugify(query.split('\t')[1]) + '_' + query.split('\t')[6] == form["query"].value:
			queries.pop(i)
			break

	with open('./interrogar-ud/queries.txt','w') as f:
		f.write("\n".join(queries))

	print('<body onload="redirect()"><script>function redirect() { window.location = "../cgi-bin/interrogatorio.py" }</script></body>')

else:
	with open('./interrogar-ud/queries.txt', 'r', encoding="utf-8") as f:
		queries = f.read().splitlines()
	for i, query in enumerate(queries):
		if slugify(query.split('\t')[1]) + '_' + query.split('\t')[6] == form["query"].value:
			queries.pop(i)
			break

	with open('./interrogar-ud/queries.txt','w') as f:
		f.write("\n".join(queries))

	print('<body onload="redirect()"><script>function redirect() { window.location = "../cgi-bin/interrogatorio.py" }</script></body>')




