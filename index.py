#!/usr/bin/python3
print('Content-type:text/html')
print('\n\n')

print('<head><title>ComCorHd</title></head><body>')

import os
for pasta in os.listdir('.'):
	if os.path.isdir(pasta) and pasta != 'cgi-bin' and pasta[0] != '.':
		print('<h1><a href="' + pasta + '">' + pasta + '</a></h1><hr>')

print('<script>window.location = "/interrogar-ud/";</script></body>')
