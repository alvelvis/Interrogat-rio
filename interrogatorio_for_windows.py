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

dirs = "interrogar-ud cgi-bin".split()

for dir in dirs:
    root_src_dir = "www/{}".format(dir)
    root_dst_dir = dir
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                # in case of the src and dst are the same file
                if os.path.samefile(src_file, dst_file):
                    continue
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir)

os.environ['PYTHONUTF8'] = "1"
print("\n=== INTERROGATÓRIO ===\n\n>>> Open 'http://localhost:8000' on your browser to access Interrogatório locally.\n")

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "www"))
CGIHTTPRequestHandler.cgi_directories = ['/cgi-bin']
httpd = HTTPServer(('', 8000), CGIHTTPRequestHandler)

webbrowser.open('http://localhost:8000')
httpd.serve_forever()