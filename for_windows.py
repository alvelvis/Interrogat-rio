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
from http.server import HTTPServer, CGIHTTPRequestHandler

def main():

    try:
        import GitPython
    except:
        os.system("\"{}\\python.exe\" -m pip install -r requirements.txt".format(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Python39")))

    os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PortableGit", "bin", "git.exe")
    os.environ['PYTHONUTF8'] = "1"
    path = os.path.dirname(os.path.abspath(__file__))

    try:
        from git import Repo
        repo = Repo('{}'.format(path))
        current = repo.head.commit
        repo.config_writer().set_value("user", "name", "myusername").release()
        repo.config_writer().set_value("user", "email", "myemail").release()
        repo.config_writer().set_value("core", "fileMode", "false").release()
        repo.config_writer().set_value("core", "autocrlf", "true").release()
        repo.git.pull()
        if current != repo.head.commit:
            print("Interrogatório was updated. Please, open it again.")
            sys.exit()
    except Exception as e:
        print("Warning (Git): {}".format(e))
    
    print("\n=== INTERROGATÓRIO ===\n\n>>> Open 'http://localhost:8000' on your browser to access Interrogatório locally.\n")
    if not 'www' in os.getcwd():
        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "www"))
        server_object = HTTPServer(('', 8000), CGIHTTPRequestHandler)
        webbrowser.open('http://localhost:8000')
        server_object.serve_forever()
    
main()