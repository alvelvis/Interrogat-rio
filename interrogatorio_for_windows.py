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
    repo = Repo('{}'.format(path))
    repo.config_writer().set_value("user", "name", "myusername").release()
    repo.config_writer().set_value("user", "email", "myemail").release()
    repo.git.pull()
    
    sys.stderr.write("\n=== INTERROGATÓRIO ===\n\n>>> Open 'http://localhost:8000' on your browser to access Interrogatório locally.\n")

    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    if not is_port_in_use(8000):
        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "www"))
        server_object = HTTPServer(server_address=('', 8000), RequestHandlerClass=CGIHTTPRequestHandler)
        webbrowser.open('http://localhost:8000')
        server_object.serve_forever()
    else:
        sys.stderr.write("\n\nPort 8000 already in use.")

main()