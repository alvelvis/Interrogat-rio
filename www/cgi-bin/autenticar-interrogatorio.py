#!/usr/bin/env python3

print('Content-type:text/html\n\n')
import os
import cgi, cgitb
cgitb.enable()

if os.environ['REQUEST_METHOD'] == 'POST':
	form = cgi.FieldStorage()
	if not os.path.isfile('./interrogar-ud/credenciais.txt'):
		with open('./interrogar-ud/credenciais.txt', 'w') as f:
			f.write('')
	with open('./interrogar-ud/credenciais.txt', 'r') as f:
		credenciais = f.read().splitlines()
	if form['nome'].value in credenciais and form['senha'].value == 'unicornio':
		if not "HTTP_COOKIE" in os.environ: os.environ["HTTP_COOKIE"] = "conectado=true"
		print('<script>\ndocument.cookie = "conectado=true; expires=2030; path=./cgi-bin/inquerito.py";\nwindow.alert("Credenciado com sucesso!\\nBem-vindo/a, ' + form['nome'].value + '.");\nwindow.close();\n</script>')
	else:
		print('Acesso não autorizado.')
