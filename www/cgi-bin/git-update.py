#!/usr/bin/python3
# -*- coding: UTF-8 -*-

print("Content-type:text/html; charset=utf-8")
print('\n\n')

import os
import cgi, cgitb
cgitb.enable()

os.system("git pull")
print("ok")
