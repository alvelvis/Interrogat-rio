import os
import chardet
import dill
import simplejson
import regex
import sys
import subprocess
import webbrowser
import shutil
from git import Repo
from http.server import HTTPServer, CGIHTTPRequestHandler

path = os.path.dirname(os.path.abspath(__file__))
repo = Repo('{}'.format(path))
repo.config_writer().set_value("user", "name", "myusername").release()
repo.config_writer().set_value("user", "email", "myemail").release()
repo.git.pull()

os.environ['PYTHONUTF8'] = "1"
print("\n=== INTERROGATÓRIO ===\n\n>>> Open 'http://localhost:8000' on your browser to access Interrogatório locally.\n")

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "www"))
CGIHTTPRequestHandler.cgi_directories = ['/cgi-bin']
httpd = HTTPServer(('', 8000), CGIHTTPRequestHandler)

webbrowser.open('http://localhost:8000')
httpd.serve_forever()
