#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html")
print('\n\n')

import os, sys
import cgi,cgitb
cgitb.enable()
import datetime
import subprocess
import requests
import charset_normalizer
import html as web
from estrutura_dados import slugify as slugify
from utils import prettyDate
from max_upload import max_filesize
if 'win' in sys.platform:
    from tkinter import Tk     # from tkinter import Tk for Python 3.x
    from tkinter.filedialog import askopenfilename

JULGAMENTO = False
if os.path.isdir("../Julgamento/static/uploads"):
    JULGAMENTO = "../Julgamento"
if os.path.isdir("../../Julgamento/static/uploads"):
    JULGAMENTO = "../../Julgamento"

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
    with open('./interrogar-ud/arquivo_ud.html', 'r') as f:
        html = f.read()
    if JULGAMENTO:
        html = html.replace("<!--JULGAMENTO", "<").replace("JULGAMENTO-->", ">")

    response = requests.get("http://lindat.mff.cuni.cz/services/udpipe/api/models")
    json_data = [name for name, values in response.json()['models'].items() if all(x in values for x in "tokenizer,tagger,parser".split(","))]
    udpipe_models = "\n".join(["<option {}>{}</option>".format('selected="selected"' if 'petrogold-ud-2.12' in x else '', x) for x in json_data])

    if 'win' in sys.platform:
        html = html.replace("<!--INPUT-->", '<input value="Escolher arquivo" class="translateVal" type="submit">')
        html = html.replace('<select id="chooseLanguage" name="chooseLanguage" style="margin-top: 10px; margin-bottom: 10px; display:none">', '<span class="translateHtml">Modelo para anotação de arquivos .txt</span>: <select id="chooseLanguage" name="chooseLanguage" style="margin-top: 10px; margin-bottom: 10px;">')
    else:
        html = html.replace("<!--INPUT-->", '<input name="file" value="Escolher arquivo" class="translateVal uploadFile" required="required" type="file">')
    html = html.replace("<!--chooseLanguage-->", udpipe_models)

    html1 = html.split('<!--SPLIT-->')[0]
    html2 = html.split('<!--SPLIT-->')[1]

    if not os.path.isdir('./interrogar-ud/conllu'):
        os.mkdir('./interrogar-ud/conllu')

    uds = [x for x in os.listdir('./interrogar-ud/conllu') if os.path.isfile('./interrogar-ud/conllu/' + x) if x != "README.md" and x.endswith(".conllu")]

    for ud in sorted(uds, key=lambda x: x.lower()):
        html1 += f'<div class="container-lr"><b>{web.escape(ud.rsplit(".conllu")[0])}</b> &nbsp;&nbsp; <span ud="{web.escape(ud)}" size="{str(file_size("./interrogar-ud/conllu/" + ud)).split(" ")[0]}" class="n_sent">carregando...</span> <span class="translateHtml">frases</span> &nbsp;&nbsp; <span ud="{web.escape(ud)}" class="n_tokens">carregando...</span> tokens &nbsp;&nbsp; <span ud="{web.escape(ud)}" class="n_columns">carregando...</span> <span class="translateHtml">colunas</span> &nbsp;&nbsp; <span ud="{web.escape(ud)}" class="n_files">carregando...</span> <span class="translateHtml">arquivos</span> &nbsp;&nbsp; ' + str(file_size('./interrogar-ud/conllu/' + ud)) + ' &nbsp;&nbsp; ' + prettyDate(str(datetime.datetime.fromtimestamp(os.path.getctime('./interrogar-ud/conllu/' + ud)))).beautifyDateDMAH() + f''' &nbsp;&nbsp;&nbsp; [ <a href="../interrogar-ud/conllu/{web.escape(ud)}" title="Fazer download do corpus" download>download</a> | <a class="translateHtml updateCorpus" ud="{web.escape(ud)}" href="#" title="Atualizar informações sobre o corpus, como número de tokens e frases">atualizar</a> | <a class="translateHtml" ud="{web.escape(ud)}" target="_blank" href="../cgi-bin/gerenciar_colunas.py?conllu={web.escape(ud)}" title="Gerenciar, adicionar ou remover colunas do corpus">colunas</a><!--a target="_blank" class="translateHtml" href="../cgi-bin/arquivo_ud.py?validate=''' + web.escape(ud) + '''">| validar</a--> | <a class="translateHtml" href="#" onclick='apagarCorpus("''' + web.escape(ud) + '''")' title="Excluir corpus do Interrogatório">excluir</a> ]</div>\n'''

    novo_html = html1 + "<script>loadCorpora()</script>" + html2

    print(novo_html)


elif not 'validate' in form:

    def reload():
        print("<script>window.location.href = '../cgi-bin/arquivo_ud.py'</script>")

    def save_file(filename, filename_path, file_content):
        if os.path.isfile(filename_path):
            print("Arquivo \"" + filename + "\" já existe no repositório.")
        else:
            with open(filename_path, 'w', encoding="utf-8") as f:
                f.write(file_content)
            if JULGAMENTO:
                with open(JULGAMENTO + "/static/uploads/" + filename.rsplit(".", 1)[0] + "_original.conllu", 'w', encoding='utf-8') as e:
                    e.write(file_content)
            reload()

    def process_text(filename, filename_path, file_content):
        if os.path.isfile(filename_path.rsplit(".txt", 1)[0] + ".conllu"):
            print("Arquivo \"" + filename.rsplit(".txt", 1)[0] + ".conllu" + "\" já existe no repositório.")
        else:
            url = "http://lindat.mff.cuni.cz/services/udpipe/api/process"
            files = {'data': file_content}
            data = {
                'tokenizer': '',
                'tagger': '',
                'parser': '',
                'model': form['chooseLanguage'].value
            }
            response = requests.post(url, files=files, data=data)
            processed = response.json()['result']

            with open(filename_path.rsplit(".", 1)[0] + ".conllu", "w") as f:
                f.write(processed)

            if JULGAMENTO:
                with open(JULGAMENTO + "/static/uploads/" + filename.rsplit(".", 1)[0] + "_original.conllu", 'w') as f:
                    f.write(processed)
            reload()

    if 'win' in sys.platform:
        root = Tk()
        root.attributes("-topmost", True)
        root.withdraw() # we don't want a full GUI, so keep the root window from appearing
        windows_path = askopenfilename(title="Select a CoNLL-U or a TXT file", filetypes=[("CoNLL-U or Text file", "*.conllu; *.txt")],) # show an "Open" dialog box and return the path to the selected file
        if windows_path:
            filename = slugify(os.path.basename(windows_path))
            file_content = str(charset_normalizer.from_path(windows_path).best()).replace("\r\n", "\n").strip() + "\n\n"
            filename_path = "./interrogar-ud/conllu/" + filename
            if filename.endswith(".conllu"):
                save_file(filename, filename_path, file_content)
            elif filename.endswith(".txt"):
                process_text(filename, filename_path, file_content)
            else:
                print("Arquivo não está no formato indicado.")
        else:
            reload()
    else:
        fileitem = form['file'].file
        fileitem.seek(0, 2) # Seek to the end of the file.
        filesize = fileitem.tell() # Get the position of EOF.
        fileitem.seek(0) # Reset the file position to the beginning.s
        if filesize <= 0: #max_filesize:
            print(f"Arquivo maior que {str(max_filesize)[:-6]}mb não suportado.")
        else:
            with open("needs_converting", "wb") as f:
                f.write(form['file'].file.read())
            file_content = str(charset_normalizer.from_path("needs_converting").best()).strip() + "\n\n"
            os.remove("needs_converting")
            filename = slugify(form['file'].filename)
            filename_path = './interrogar-ud/conllu/' + filename

            if filename.endswith(".conllu"):
                save_file(filename, filename_path, file_content)
            elif filename.endswith(".txt"):
                process_text(filename, filename_path, file_content)
            else:
                print('Arquivo não está no formato indicado.')
else:
    print('<html><head><meta charset="UTF-8"><title>validate.py</title></head><body>')
    try:
        output = subprocess.check_output('python3 ./cgi-bin/tools/validate.py --max-err=0 --lang=pt ./interrogar-ud/conllu/' + form['validate'].value, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
    for line in output.split('\n'):
        print('<br>', line)
    print('</body></html>')


