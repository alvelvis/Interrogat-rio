#!/usr/bin/python3

print('Content-type:text/html\n\n')
import os
import cgi, cgitb
cgitb.enable()

if os.environ['REQUEST_METHOD'] == 'POST':
	form = cgi.FieldStorage()
	if not os.path.isfile('/interrogar-ud/credenciais.txt'):
		open('/interrogar-ud/credenciais.txt', 'w').write('')
	credenciais = open('/interrogar-ud/credenciais.txt', 'r').read().splitlines()
	if form['nome'].value in credenciais and form['senha'].value == 'unicornio':
		print('<script>\ndocument.cookie = "conectado=true; expires=2030; domain=.comcorhd.tronco.me; path=/cgi-bin/inquerito.py";\nwindow.alert("Credenciado com sucesso!\\nBem-vindo/a, ' + form['nome'].value + '.");\nwindow.close();\n</script>')
	else:
		print('Acesso não autorizado.')
