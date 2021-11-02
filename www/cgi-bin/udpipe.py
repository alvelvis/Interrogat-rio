#!../.interrogatorio/bin/python3
print('Content-type:text/html\n\n')

import os
import cgi, cgitb
cgitb.enable()
import estrutura_dados
import functions

modelo = functions.modelo
udpipe = functions.udpipe

html = '<html><head><script src=\"../interrogar-ud/jquery-latest.js\"></script><script src=\"../interrogar-ud/resultados.js?version=15\"></script><meta name="viewport" http-equiv="content-type" content="text/html; charset=UTF-8; width=device-width, initial-scale=1.0"><title class="translateHtml">UDPipe: Interrogatório</title></head><body>'

if os.environ['REQUEST_METHOD'] == 'POST':
	form = cgi.FieldStorage()
	ud = form['conllu'].value
	text = form['textheader'].value

	html += '<style>body { width: 90%; margin: 20px auto; }</style><h1>UDPipe</h1><hr><a href="#" class="translateHtml" onclick="window.close();">Fechar</a><br><br>'
	html += '<span class="translateHtml">Modelo:</span> <a href="../cgi-bin/' + modelo + '" download>' + modelo + '</a>'
	html += '<br>Corpus: <a href="../interrogar-ud/conllu/' + ud + '" download>' + ud + '</a>'

	with open('./cgi-bin/cru.txt', 'w') as f:
		f.write(text.replace('"', '\\"'))

	os.system('cat ./cgi-bin/cru.txt | ./cgi-bin/' + udpipe + ' --tokenize --tag --parse ./cgi-bin/' + modelo + ' > ./cgi-bin/anotado.txt')

	with open('./cgi-bin/anotado.txt', 'r') as f:
		resultado = f.read()

	os.remove("./cgi-bin/cru.txt")
	os.remove("./cgi-bin/anotado.txt")

	html += '<pre style="font-size: 14px">' + resultado + '</pre>'

	anotado = estrutura_dados.LerUD('./interrogar-ud/conllu/' + ud)
	for sentence in anotado:
		if '# text = ' + text in sentence:
			anotado = sentence
			break

	for a, linha in enumerate(anotado):
		if isinstance(linha, list):
			anotado[a] = '\t'.join(anotado[a])
	anotado = '\n'.join(anotado)

	#html += '''<br><input type=button value="Mostrar anotação original (''' + ud + ''')" onclick="document.getElementById('anotacao').style.display = 'block';"><pre id=anotacao style="display:none"><br>''' + anotado + '''</pre>'''

	#os.remove('./interrogar-ud/anotado.txt')

html += '</body></html>'
print(html)
