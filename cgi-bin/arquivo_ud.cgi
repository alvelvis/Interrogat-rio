#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html")
print('\n\n')

import os
import cgi,cgitb
cgitb.enable()
import re
import datetime
from estrutura_dados import slugify as slugify
import subprocess

#if not 'REQUEST_METHOD' in os.environ:
#	os.environ['REQUEST_METHOD'] = 'POST'

form = cgi.FieldStorage()

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)

if os.environ['REQUEST_METHOD'] != 'POST' and not 'validate' in form:
    html = open('/interrogar-ud/arquivo_ud.html', 'r').read()
    html1 = html.split('<!--SPLIT-->')[0]
    html2 = html.split('<!--SPLIT-->')[1]

    if not os.path.isdir('/interrogar-ud/conllu'):
        os.mkdir('/interrogar-ud/conllu')

    uds = [x for x in os.listdir('/interrogar-ud/conllu') if os.path.isfile('/interrogar-ud/conllu/' + x)]

    for ud in uds:
        try:
            leitura = open('/interrogar-ud/conllu/' + ud, 'r').read()
            n_sent = str(len(leitura.split('\n\n')))
            n_tokens = 0
            for linha in leitura.splitlines():
            	if len(linha.split('\t')) > 2:
            		n_tokens += 1
            html1 += '<div class="container-lr"><a href="/interrogar-ud/conllu/' + ud + '" download>' + ud + '</a> &nbsp;&nbsp; ' + n_sent + ' sentenças &nbsp;&nbsp; ' + str(n_tokens) + ' tokens &nbsp;&nbsp; ' + str(file_size('/interrogar-ud/conllu/' + ud)) + ' &nbsp;&nbsp; ' + str(datetime.datetime.fromtimestamp(os.path.getctime('/interrogar-ud/conllu/' + ud))).split('.')[0] + ''' &nbsp;&nbsp;&nbsp; <a href="#" onclick='apagar("''' + ud + '''")' >excluir</a> | <a target="_blank" href="/cgi-bin/arquivo_ud.cgi?validate=''' + ud + '''">validar</a></div>\n'''
        except:
            html1 += '<div class="container-lr"><a href="/interrogar-ud/conllu/' + ud + '" download>' + ud + '</a> &nbsp;&nbsp; MemoryError &nbsp;&nbsp; ' + str(file_size('/interrogar-ud/conllu/' + ud)) + ' &nbsp;&nbsp; ' + str(datetime.datetime.fromtimestamp(os.path.getctime('/interrogar-ud/conllu/' + ud))).split('.')[0] + ''' &nbsp;&nbsp;&nbsp; <a href="#" onclick='apagar("''' + ud + '''")' >excluir</a> | <a href="/cgi-bin/arquivo_ud.cgi?validate=''' + ud + '''" target="_blank">validar</a></div>\n'''

    novo_html = html1 + html2

    print(novo_html)


elif not 'validate' in form:
    f = os.path.basename(form['file'].filename)
    open('/interrogar-ud/conllu/' + slugify(f), 'wb').write(form['file'].file.read())
    print('<body onload="redirect()"><script>function redirect() { window.location = "/cgi-bin/arquivo_ud.cgi" }</script></body>')

else:
    print('<html><head><meta charset="UTF-8"><title>validate.py</title></head><body>')
    try:
        output = subprocess.check_output('python3 /cgi-bin/validate.py --lang=pt /interrogar-ud/conllu/' + form['validate'].value, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
    for line in output.split('\n'):
        print('<br>', line)
    print('</body></html>')


