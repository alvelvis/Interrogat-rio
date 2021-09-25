import os
import chardet
import dill
import simplejson
import regex
import sys
import subprocess
import webbrowser
import shutil
import socket
from git import Repo
from http.server import HTTPServer, CGIHTTPRequestHandler

def main():

    os.environ['PYTHONUTF8'] = "1"
    path = os.path.dirname(os.path.abspath(__file__))
    print(path)
    repo = Repo('{}'.format(path))
    repo.config_writer().set_value("user", "name", "myusername").release()
    repo.config_writer().set_value("user", "email", "myemail").release()
    repo.config_writer().set_value("core", "fileMode", "false").release()
    repo.config_writer().set_value("core", "autocrlf", "true").release()
    repo.git.pull()
    
    print("\n=== INTERROGATÓRIO ===\n\n>>> Open 'http://localhost:8000' on your browser to access Interrogatório locally.\n")
    if not 'www' in os.getcwd():
        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "www"))
        server_object = HTTPServer(('', 8000), CGIHTTPRequestHandler)
        webbrowser.open('http://localhost:8000')
        server_object.serve_forever()
    
main()