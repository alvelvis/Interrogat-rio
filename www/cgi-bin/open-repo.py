#!../.interrogatorio/bin/python3
# -*- coding: UTF-8 -*-

import sys
import os
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
import os, sys, shutil
import cgi, cgitb
from estrutura_dados import slugify
cgitb.enable()

print("Content-type:text/html")
print('\n\n')

root = Tk()
root.attributes("-topmost", True)
root.withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename(title="Select a CoNLL-U file", filetypes=[("CoNLL-U file", "*.conllu")],) # show an "Open" dialog box and return the path to the selected file


def reload():
    print("<script>window.location.href = '../cgi-bin/arquivo_ud.py'</script>")

if filename:
    if not os.path.basename(filename) in os.listdir("./interrogar-ud/conllu"):
        shutil.copy(filename, "./interrogar-ud/conllu/{}".format(slugify(os.path.basename(filename))))
        reload()
    else:
        print("Arquivo já existe no repositório.")
else:
    reload()
