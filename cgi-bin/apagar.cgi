#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html")
print('\n\n')

import os
import cgi,cgitb
cgitb.enable()
from estrutura_dados import slugify as slugify

form = cgi.FieldStorage()
link = '/interrogar-ud/resultados/' + form["query"].value + '.html'

print('''<head>
           <meta http-equiv="content-type" content="text/html; charset=UTF-8">
         </head>''')

if os.path.isfile(link):
	import shutil
	os.rename(link, '/interrogar-ud/tmp/' + form['query'].value + '.html')
	if os.path.isdir('/interrogar-ud/resultados/' + form["query"].value):
		shutil.move('/interrogar-ud/resultados/' + form["query"].value, '/interrogar-ud/tmp/')
	queries = open('/interrogar-ud/queries.txt', 'r', encoding="utf-8").read().splitlines()
	for i, query in enumerate(queries):
		if slugify(query.split('\t')[1]) + '_' + query.split('\t')[6] == form["query"].value:
			queries.pop(i)
			break

	open('/interrogar-ud/queries.txt','w').write("\n".join(queries))

	print('<body onload="redirect()"><script>function redirect() { window.location = "/cgi-bin/interrogatorio.cgi" }</script></body>')

else:
	queries = open('/interrogar-ud/queries.txt', 'r', encoding="utf-8").read().splitlines()
	for i, query in enumerate(queries):
		if slugify(query.split('\t')[1]) + '_' + query.split('\t')[6] == form["query"].value:
			queries.pop(i)
			break

	open('/interrogar-ud/queries.txt','w').write("\n".join(queries))

	print('<body onload="redirect()"><script>function redirect() { window.location = "/cgi-bin/interrogatorio.cgi" }</script></body>')




