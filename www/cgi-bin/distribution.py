#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html")
print('\n\n')

import os
import cgi,cgitb
cgitb.enable()
import re
from datetime import datetime
from utils import prettyDate, encodeUrl, fastsearch, query_is_python, query_is_tokens
import datetime
import html as web
import interrogar_UD
import json

from estrutura_dados import slugify as slugify

different_distribution = ["dependentes", "children"]

#POST
form = cgi.FieldStorage()
if not 'corpus' in form:
	print("Corpus não selecionado.")
	exit()

filtros = []
nome_interrogatorio = ""
if "link_dist" in form and os.path.isfile("./cgi-bin/json/filtros.json"):
	link_interrogatorio = form['link_dist'].value.rsplit(".", 1)[0].rsplit("/", 1)[1]
	nome_interrogatorio = form['combination'].value
	with open("./cgi-bin/json/filtros.json") as f:
		filtros = json.load(f)
	if link_interrogatorio in filtros:
		filtros = [x for filtro in filtros[link_interrogatorio]['filtros'] for x in filtros[link_interrogatorio]['filtros'][filtro]['sentences']]
	else:
		filtros = []

# verifica se a busca já foi salva em um json ou se é nova (e não precisa ser salva)
json_id = form['jsonId'].value if 'jsonId' in form else None
if json_id:
	path = "./cgi-bin/json/" + json_id + ".json"
	with open(path) as f:
		json_query = json.load(f)

coluna = form['coluna'].value
dic_dist = interrogar_UD.getDistribution(json_query if json_id else ("./interrogar-ud/conllu/" + form['corpus'].value), form['notSaved'].value, filtros=filtros, coluna=coluna) # "./interrogar-ud/conllu/" + form['corpus'].value

pagina = '''
	<meta name="viewport" http-equiv="content-type" content="text/html; charset=UTF-8; width=device-width, initial-scale=1.0">
	<button onclick="topFunction()" id="myBtn" class="translateTitle translateHtml" title="Voltar ao topo">Voltar ao topo</button>
	<style>
		#myBtn {
			display: none; /* Hidden by default */
			position: fixed; /* Fixed/sticky position */
			bottom: 20px; /* Place the button at the bottom of the page */
			right: 30px; /* Place the button 30px from the right */
			z-index: 99; /* Make sure it does not overlap */
			border: none; /* Remove borders */
			outline: none; /* Remove outline */
			background-color: rgba(255,105,30,1); /* Set a background color */
			color: white; /* Text color */
			cursor: pointer; /* Add a mouse pointer on hover */
			padding: 10px 15px; /* Some padding */
			border-radius: 20px; /* Rounded corners */
			font-size: 16px; /* Increase font size */
		}

		#myBtn:hover {
			background-color: #555; /* Add a dark-grey background on hover */
		}
	</style>
	<!--script src="../interrogar-ud/jquery.min.js"></script>
	<script src="../interrogar-ud/resultados.js?version=12"></script-->
	<script>
function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("mainTable");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (dir == "asc") {
        if ((n == 0 && x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) || (n != 0 && parseFloat(x.innerHTML) > parseFloat(y.innerHTML))) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if ((n == 0 && x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) || (n != 0 && parseFloat(x.innerHTML) < parseFloat(y.innerHTML))) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
</script>
'''
pagina += "<title>Distribuição de " + coluna + ": Interrogatório</title>"
pagina += "<h1>Distribuição de " + coluna + "</h1>"
pagina += '<!--a href="#" class="translateHtml" onclick="window.close()">Fechar</a><br><br--><span class="translateHtml">Relatório gerado dia</span> ' + prettyDate(str(datetime.datetime.now())).beautifyDateDMAH() + ''
pagina += f"<hr><span class='translateHtml'>Busca:</span> <a href='../cgi-bin/interrogar.py?corpus={form['corpus'].value}&params={form['expressao'].value}'>" + web.escape(form["expressao"].value) + "</a><br>"
pagina += "<span class='translateHtml'>Corpus:</span></a> " + form["corpus"].value
pagina += "<hr><span class='translateHtml'>Quantidade de ocorrências:</span></a> "+str(dic_dist["dist"])+"<br><span class='translateHtml'>Quantidade de</span> <b>" + coluna + "</b> diferentes: "+str(len(dic_dist["lista"]))
if nome_interrogatorio and nome_interrogatorio not in fastsearch:
	pagina += f"<br><span class='translateHtml'>Busca salva em</span> <a href='../interrogar-ud/resultados/{link_interrogatorio}.html'>{nome_interrogatorio}</a>"
pagina += "<hr>"

expressao = form['expressao'].value.replace("'", '"')
parametros = expressao

if re.search(r"^\d+\s", parametros):
	criterio = int(parametros.split(" ", 1)[0])
	parametros = parametros.split(" ", 1)[1]
elif query_is_python(parametros):
	criterio = 5
else:
	criterio = 1

if criterio == 5:
	if " @" in parametros:
		identificador = parametros.rsplit(" @", 1)[1].split(" ")[0]
	elif parametros[0] == "@":
		identificador = parametros.split("@", 1)[1].split(" ")[0]
	else:
		identificador = parametros.split(" ")[0]
	identificador = "token." + identificador
	identificador = identificador.replace("token.token", "token")
	identificador = identificador.rsplit(".", 1)[0]
	if expressao[0] == "@": expressao = expressao[1:]

if criterio == 5:
	with open("./cgi-bin/dist.log", 'w') as f:
		f.write("\n".join([identificador, expressao]))

script = query_is_tokens(parametros)
pagina += f"<br><table id='mainTable' style='border-spacing: 20px 0px; margin-left:0px; text-align:left'><tr><th style='cursor:pointer' onclick='sortTable(0);'>{coluna}</th><th style='cursor:pointer' onclick='sortTable(1);' class='translateHtml'>frequência</th><th style='cursor:pointer' onclick='sortTable(2);' class='translateHtml'>em arquivos</th></tr>"
for i, dicionario in enumerate(sorted(dic_dist["lista"], key=lambda x: (-dic_dist["lista"][x], x))):
	entrada = [dicionario, dic_dist["lista"][dicionario]]
	entradaEscapada = re.escape(entrada[0])
	if not coluna in interrogar_UD.different_distribution:
		if criterio != 5 or script:
			pagina += f"<tr><td>" + web.escape(entrada[0]) + "</td><td>" + str(entrada[1]) + "</td><td>" + (str(len(dic_dist["dispersion_files"][entrada[0]])) if entrada[0] in dic_dist["dispersion_files"] else "1") + "</td></tr>"
		else:
			pagina += f"<tr><td><a target='_blank' href='../cgi-bin/interrogar.py?go=True&corpus={form['corpus'].value}&params=" + encodeUrl(expressao.replace(' @', ' ') + f" and @{identificador}.{coluna} == \"{encodeUrl(re.escape(entrada[0]))}\"") + "' title='Buscar casos: {}' style='text-decoration: none; color:blue;'>".format(web.escape(entrada[0])) + web.escape(entrada[0]) + "</a></td><td>" + str(entrada[1]) + "</td><td>" + (str(len(dic_dist["dispersion_files"][entrada[0]])) if entrada[0] in dic_dist["dispersion_files"] else "1") + "</td></tr>"
	elif coluna in ["dependentes", "children"]:	
		sent_ids = []
		for sent_id in dic_dist["all_children"][entrada[0]]:
			sent_ids.append(sent_id)
		sent_ids = '5 sentence.sent_id == "(' + ')|('.join(sent_ids) + ')" and ' + form['notSaved'].value
		if criterio == 5 and not script:
			pagina += f"<tr><td><a target='_blank' href='../cgi-bin/interrogar.py?go=True&corpus={form['corpus'].value}&params={encodeUrl(sent_ids.replace(' @', ' '))} and @{identificador}.word == \"{encodeUrl(re.escape(entrada[0].split('<b>')[1].split('</b>')[0]))}\"' title='Buscar frases: {'|'.join(dic_dist['all_children'][entrada[0]])}' style='text-decoration: none; color:blue;'>" + entrada[0] + "</a></td><td>" + str(entrada[1]) + "</td><td>" + (str(len(dic_dist["dispersion_files"][entrada[0]])) if entrada[0] in dic_dist["dispersion_files"] else "1") + "</td></tr>"
		else:
			pagina += f"<tr><td>" + entrada[0] + "</td><td>" + str(entrada[1]) + "</td><td>" + (str(len(dic_dist["dispersion_files"][entrada[0]])) if entrada[0] in dic_dist["dispersion_files"] else "1") + "</td></tr>"
pagina += "</table>"

'''
pagina += "<br><br><table style='border-spacing: 20px 0px;'><tr><th>#</th><th>"+coluna+" diferentes</th></tr>"
for entrada in sorted(lista_freq, key=lambda x: (x[1], x[0]), reverse=True):
	pagina += "<tr><td>" + str(entrada[0]) + "</td><td>" + str(entrada[1]) + "</td></tr>"
pagina += "</table>"
'''

print('<head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /></head><body>' + pagina + '<br><br></body>') #window.location="' + form['html'].value


