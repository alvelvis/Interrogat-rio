#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import os
import cgi, cgitb
cgitb.enable()

print("atualizando")
os.system("git pull")
julgamento_folder = ["../Julgamento/", "../../Julgamento/", "../../../Julgamento"]
for folder in julgamento_folder:
	if os.path.isdir(folder):
		os.system(f"cd {folder}; git pull")
print("ok")
