#!/usr/bin/python3
print('Content-type:text/html\n\n')

import os
import cgi, cgitb
cgitb.enable()
import estrutura_dados

modelo = 'bosque-2.3.udpipe'

html = '<html><head><meta name="viewport" http-equiv="content-type" content="text/html; charset=UTF-8; width=device-width, initial-scale=1.0"><title>UDPipe: Interrogatório</title></head><body>'

if os.environ['REQUEST_METHOD'] == 'POST':
	form = cgi.FieldStorage()
	ud = form['conllu'].value
	text = form['textheader'].value

	html += '<style>body { width: 90%; margin: 20px auto; }</style><h1>UDPipe</h1><hr><a href="#" onclick="window.close()"">Fechar</a><br><br>'
	html += 'Modelo: <a href="/interrogar-ud/modelos_udpipe/' + modelo + '" download>' + modelo + '</a>'

	open('/interrogar-ud/cru.txt', 'w').write(text.replace('"', '\\"'))

	os.system('cat /interrogar-ud/cru.txt | /interrogar-ud/udpipe --tokenize --tag --parse /interrogar-ud/modelos_udpipe/' + modelo + ' > /interrogar-ud/anotado.txt')

	resultado = open('/interrogar-ud/anotado.txt', 'r').read()

	html += '<pre style="font-size: 14px">' + resultado + '</pre>'

	anotado = estrutura_dados.LerUD('/interrogar-ud/conllu/' + ud)
	for sentence in anotado:
		if '# text = ' + text in sentence:
			anotado = sentence
			break

	for a, linha in enumerate(anotado):
		if isinstance(linha, list):
			anotado[a] = '\t'.join(anotado[a])
	anotado = '\n'.join(anotado)

	#html += '''<br><input type=button value="Mostrar anotação original (''' + ud + ''')" onclick="document.getElementById('anotacao').style.display = 'block';"><pre id=anotacao style="display:none"><br>''' + anotado + '''</pre>'''

	#os.remove('/interrogar-ud/anotado.txt')

html += '</body></html>'
print(html)
