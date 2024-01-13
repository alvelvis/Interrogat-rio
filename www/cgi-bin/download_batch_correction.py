#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import cgi,cgitb
cgitb.enable()
from utils import query_is_python, query_is_tokens

with open("./interrogar-ud/scripts/modelo_batch_correction.txt") as f:
    script = f.read().splitlines()

form = cgi.FieldStorage()

empty_line = script.index('') + 1

parametros = form['params'].value if 'params' in form else ""
if query_is_tokens(parametros):
    script[empty_line] = 'bold_tokens = %s' % parametros.split("tokens=")[1].split("|")
    script[empty_line] += "\n"
    script[empty_line] += 'bold_tokens = [{"sent_id": x.split(":")[0], "token_ids": x.split(":")[1].split(",")} for x in bold_tokens]'
    script[empty_line] += "\n\n"
    script[empty_line] += "if any(sentence.sent_id == x['sent_id'] and token.id in x['token_ids'] for x in bold_tokens):"
elif query_is_python(parametros):
    script[empty_line] = 'if ' + parametros.replace('re.search( r"^(" + r', 'regex(').replace(' + r")$"', '').replace(".__dict__['", ".").replace("'] ", "") + ":"

with open("./interrogar-ud/scripts/modelo-batch.txt", "w") as f:
    f.write("\n".join(script))

print('''
<a href="../interrogar-ud/scripts/modelo-batch.txt" id="download" download >Initiate download from link</a>
<a href="#" id="close" onclick="window.close()" ><br>Close tab</a>
<script type="text/javascript">
    // initiate download by script
    // add this in onload event or after the iframe
    document.getElementById('download').click();
    setTimeout(function(){ window.close(); }, 2000 )
</script>
''')