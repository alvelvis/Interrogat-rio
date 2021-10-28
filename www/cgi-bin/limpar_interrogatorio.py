#!/usr/bin/env python3

print('Content-type:text/html\n\n')

from datetime import datetime
import os
import shutil
import cgitb
cgitb.enable()

if os.path.isfile('./interrogar-ud/inqueritos-log.txt'):
	with open('./interrogar-ud/inqueritos-log.txt', 'r') as f:
		logfile = f.read()
else:
	with open('./interrogar-ud/inqueritos-log.txt', 'w') as f:
		f.write('')
	with open('./interrogar-ud/inqueritos-log.txt', 'r') as f:
		logfile = f.read()

log = list()

for arquivo in os.listdir('./interrogar-ud/conllu'):
	if arquivo.startswith("tmp_"):
		os.remove("./interrogar-ud/conllu/" + arquivo)
		log.append(f"- corpus {arquivo} removido")

#apaga tmp
if os.path.isdir('./interrogar-ud/tmp'):
	shutil.rmtree('./interrogar-ud/tmp')
	os.mkdir('./interrogar-ud/tmp')
	with open("./interrogar-ud/tmp/README", "w") as f:
		f.write('temporary files')
	log.append('- /interrogar-ud/tmp excluída e recriada')
else:
	os.mkdir('./interrogar-ud/tmp')
	log.append('- /interrogar-ud/tmp criada')

'''
#apaga se antes = depois ou depois not in ud
with open('./interrogar-ud/inqueritos.txt', 'r') as f:
	inqueritos = f.read().splitlines()
novo_inqueritos = list()
for inquerito in inqueritos:
	if inquerito and inquerito.split('!@#')[1].split(' --> ')[0] == inquerito.split('!@#')[1].split(' --> ')[1].replace('<b>','').replace('</b>',''):
		log.append('- inquérito excluído (não modificou nada): ' + inquerito)
		continue
	#elif inquerito and not inquerito.split('!@#')[1].split(' --> ')[1].replace('<b>','').replace('</b>','') in open('/interrogar-ud/conllu/' + inquerito.split('!@#')[2], 'r').read():
		#log.append('- inquérito excluído (modificação não se manteve): ' + inquerito)
		#continue
	else:
		novo_inqueritos.append(inquerito)
with open('./interrogar-ud/inqueritos.txt', 'w') as f:
	f.write('\n'.join(novo_inqueritos))
'''

#etiquetas dos inquéritos
with open('./interrogar-ud/inqueritos_cars.txt', 'r') as f:
	inqueritos_cars = f.read().splitlines()
with open('./interrogar-ud/inqueritos.txt', 'r') as f:
	inqueritos = f.read()
novo_inqueritos_cars = list()
for inquerito_car in inqueritos_cars:
	if ('!@#' + inquerito_car not in inqueritos or 'teste' in inquerito_car) and inquerito_car:
		log.append('- etiqueta de inquérito excluída: ' + inquerito_car)
		continue
	else:
		novo_inqueritos_cars.append(inquerito_car)
with open('./interrogar-ud/inqueritos_cars.txt', 'w') as f:
	f.write('\n'.join(novo_inqueritos_cars))

#pesquisas se 'teste' in nome
with open('./interrogar-ud/queries.txt', 'r') as f:
	queries = f.read().splitlines()
novo_queries = list()
for query in queries:
	if query and 'teste' == query.split('\t')[1]:
		if query and os.path.isdir(query.split('\t')[0].split('.html')[0]):
			shutil.rmtree(query.split('\t')[0].split('.html')[0])
			log.append('- diretório excluído: ' + query.split('\t')[0].split('.html')[0])
		if os.path.isfile(query.split('\t')[0]): os.remove(query.split('\t')[0])
		log.append('- entrada de pesquisa e pesquisa excluídas: ' + query)
		continue
	else:
		novo_queries.append(query)
with open('./interrogar-ud/queries.txt', 'w') as f:
	f.write('\n'.join(novo_queries))

#apaga resultados sem entrada nas queries
with open('./interrogar-ud/queries.txt', 'r') as f:
	queries = f.read()
for item in os.listdir('./interrogar-ud/resultados'):
	if not item in queries and item.strip() != '' and item != 'link1.html':
		if os.path.isfile('./interrogar-ud/resultados/' + item):
			os.remove('./interrogar-ud/resultados/' + item)
			log.append('- pesquisa excluída (não encontrada em queries): ' + query)
		elif os.path.isdir('./interrogar-ud/resultados/' + item):
			shutil.rmtree('./interrogar-ud/resultados/' + item)
			log.append('- diretório excluído (não encontrado em queries): ' + query)

with open('./interrogar-ud/inqueritos-log.txt', 'w') as f:
	f.write(str(datetime.now()).replace(' ','_').split('.')[0] + ':\n' + '\n'.join(log) + '\n\n' + logfile)
print('<pre>' + str(datetime.now()).replace(' ','_').split('.')[0] + ':\n' + '\n'.join(log) + '</pre>')
