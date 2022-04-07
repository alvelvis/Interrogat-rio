#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import sys
import cgi,cgitb
cgitb.enable()
import re, html, time
from functions import prettyDate
import html as web

with open("./interrogar-ud/scripts/modelo_script.txt") as f:
    script = f.read().splitlines()

form = cgi.FieldStorage()

empty_line = script.index('') + 1

if form['crit'].value == '5':
    script[empty_line] = 'if ' + form['params'].value.replace('re.search( r"^(" + r', 'regex(').replace(' + r")$"', '').replace(".__dict__['", ".").replace("'] ", "") + ":"

with open("./interrogar-ud/scripts/interrogar-script.txt", "w") as f:
    f.write("\n".join(script))

print('''
<a href="../interrogar-ud/scripts/interrogar-script.txt" id="download" download >Initiate download from link</a>
<a href="#" id="close" onclick="window.close()" ><br>Close tab</a>
<script type="text/javascript">
    // initiate download by script
    // add this in onload event or after the iframe
    document.getElementById('download').click();
    setTimeout(function(){ window.close(); }, 2000 )
</script>
''')