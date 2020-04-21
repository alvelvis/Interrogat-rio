#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html")
print('\n\n')

import os, sys
import cgi,cgitb
cgitb.enable()
import re
import datetime
from estrutura_dados import slugify as slugify
import subprocess
from functions import prettyDate
import functions
from chardet import detect
from max_upload import max_filesize

JULGAMENTO = False
if os.path.isdir("../../Julgamento"):
    JULGAMENTO = "../../Julgamento"
if os.path.isdir("../../../Julgamento"):
    JULGAMENTO = "../../../Julgamento"

def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']

form = cgi.FieldStorage()

def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)

if os.environ['REQUEST_METHOD'] != 'POST' and not 'validate' in form:
    html = open('../interrogar-ud/arquivo_ud.html', 'r').read()
    if JULGAMENTO:
        html = html.replace("<!--JULGAMENTO", "<").replace("JULGAMENTO-->", ">")

    html1 = html.split('<!--SPLIT-->')[0]
    html2 = html.split('<!--SPLIT-->')[1]

    if not os.path.isdir('../interrogar-ud/conllu'):
        os.mkdir('../interrogar-ud/conllu')

    uds = [x for x in os.listdir('../interrogar-ud/conllu') if os.path.isfile('../interrogar-ud/conllu/' + x)]

    for ud in sorted(uds):
        if ud != 'README':
            html1 += '<div class="container-lr"><a href="../interrogar-ud/conllu/' + ud + '" download>' + ud + f'</a> &nbsp;&nbsp; <span ud="{ud}" class="n_sent">carregando...</span> <span class="translateHtml">sentenças</span> &nbsp;&nbsp; <span ud="{ud}" class="n_tokens">carregando...</span> tokens &nbsp;&nbsp; ' + str(file_size('../interrogar-ud/conllu/' + ud)) + ' &nbsp;&nbsp; ' + prettyDate(str(datetime.datetime.fromtimestamp(os.path.getctime('../interrogar-ud/conllu/' + ud)))).beautifyDateDMAH() + ''' &nbsp;&nbsp;&nbsp; <a class="translateHtml" href="#" onclick='apagarCorpus("''' + ud + '''")' >excluir</a> | <a target="_blank" class="translateHtml" href="../cgi-bin/arquivo_ud.cgi?validate=''' + ud + '''">validar</a></div>\n'''

    novo_html = html1 + "<script>loadCorpora()</script>" + html2

    print(novo_html)


elif not 'validate' in form:
    fileitem = form['file'].file
    fileitem.seek(0, 2) # Seek to the end of the file.
    filesize = fileitem.tell() # Get the position of EOF.
    fileitem.seek(0) # Reset the file position to the beginning.
    f = os.path.basename(form['file'].filename)
    if filesize > max_filesize:
        print(f"Arquivo maior que {str(max_filesize)[:-6]}mb não suportado.")
    else:
        if form['file'].filename.endswith('.conllu'):
            if os.path.isfile('../interrogar-ud/conllu/' + slugify(f)):
                print("Arquivo \"" + slugify(f) + "\" já existe no repositório.")
            else:
                open('../interrogar-ud/conllu/' + slugify(f), 'wb').write(form['file'].file.read())
                srcfile = '../interrogar-ud/conllu/' + slugify(f)
                trgfile = 'codification'
                from_codec = get_encoding_type(srcfile)
                with open(srcfile, 'r', encoding=from_codec) as ff, open(trgfile, 'w', encoding='utf-8') as e:
                    text = ff.read() # for small files, for big use chunks
                    e.write(text)
                if JULGAMENTO:
                    with open(srcfile, 'r', encoding=from_codec) as ff, open(JULGAMENTO + "/static/uploads/" + slugify(f).rsplit(".", 1)[0] + "_original.conllu", 'w', encoding='utf-8') as e:
                        text = ff.read() # for small files, for big use chunks
                        e.write(text)
                os.remove(srcfile) # remove old encoding file
                os.rename(trgfile, srcfile) # rename new encoding
                print('<body onload="redirect()"><script>function redirect() { window.location = "../cgi-bin/arquivo_ud.cgi" }</script></body>')
        elif form['file'].filename.endswith(".txt"):
            if os.path.isfile('../interrogar-ud/conllu/' + slugify(f).rsplit(".txt", 1)[0] + ".conllu"):
                print("Arquivo \"" + slugify(f).rsplit(".txt", 1)[0] + ".conllu" + "\" já existe no repositório.")
            else:
                open('../interrogar-ud/conllu/' + slugify(f), 'wb').write(form['file'].file.read())
                srcfile = '../interrogar-ud/conllu/' + slugify(f)
                trgfile = 'codification'
                from_codec = get_encoding_type(srcfile)
                with open(srcfile, 'r', encoding=from_codec) as ff, open(trgfile, 'w', encoding='utf-8') as e:
                    text = ff.read() # for small files, for big use chunks
                    e.write(text)
                os.remove(srcfile) # remove old encoding file
                os.rename(trgfile, srcfile) # rename new encoding
                os.system('cat ../interrogar-ud/conllu/' + slugify(f) + ' | ../cgi-bin/' + functions.udpipe + ' --tokenize --tag --parse ../cgi-bin/' + functions.modelo + ' > ../interrogar-ud/conllu/' + slugify(f).rsplit(".", 1)[0] + ".conllu")
                os.system('rm ../interrogar-ud/conllu/' + slugify(f))
                if JULGAMENTO:
                    with open('../interrogar-ud/conllu/' + slugify(f).rsplit(".", 1)[0] + ".conllu") as ff, open(JULGAMENTO + "/static/uploads/" + slugify(f).rsplit(".", 1)[0] + "_original.conllu", 'w') as e:
                        text = ff.read() # for small files, for big use chunks
                        e.write(text)
                print('<body onload="redirect()"><script>function redirect() { window.location = "../cgi-bin/arquivo_ud.cgi" }</script></body>')
        else:
            print('Arquivo não está no formato indicado.')

else:
    print('<html><head><meta charset="UTF-8"><title>validate.py</title></head><body>')
    try:
        output = subprocess.check_output('python3 ../cgi-bin/tools/validate.py --max-err=0 --lang=pt ../interrogar-ud/conllu/' + form['validate'].value, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
    for line in output.split('\n'):
        print('<br>', line)
    print('</body></html>')


