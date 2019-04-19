#!/usr/bin/python
# -*- coding: UTF-8 -*-

print("Content-type:text/html")
print('\n\n')

import os
import cgi

form = cgi.FieldStorage()
link = '/interrogar-ud/conllu/' + form["ud"].value

print('''<head>
           <meta http-equiv="content-type" content="text/html; charset=UTF-8">
         </head>''')

if os.path.isfile(link):
	os.rename(link, '/interrogar-ud/tmp/' + form["ud"].value)

	print('<body onload="redirect()"><script>function redirect() { window.location = "/cgi-bin/arquivo_ud.cgi" }</script></body>')
else:
	print('Arquivo "' + link + '" não existe.')
