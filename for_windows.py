import os
import sys
import webbrowser
from http.server import HTTPServer, CGIHTTPRequestHandler

def main():
    
    branch = None
    if len(sys.argv) >= 2:
        branch = "master" if sys.argv[1] == "stable" else sys.argv[1]

    # to make a new update that requires new packages: append the name of the package in the list and try to import it
    new_packages = "GitPython udapi langchain openai".split(" ")
    try:
        exec("import {}".format(new_packages[-1]))
    except:
        for package in new_packages:
            os.system("\"{}\\python.exe\" -m pip install {}".format(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Python39"), package))

    os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PortableGit", "bin", "git.exe")
    os.environ['PYTHONUTF8'] = "1"
    path = os.path.dirname(os.path.abspath(__file__))

    try:
        from git import Repo
        repo = Repo(path)
        current = repo.head.commit
        repo.config_writer().set_value("user", "name", "myusername").release()
        repo.config_writer().set_value("user", "email", "myemail").release()
        repo.config_writer().set_value("core", "fileMode", "false").release()
        repo.config_writer().set_value("core", "autocrlf", "true").release()
        repo.git.pull()
        if current != repo.head.commit:
            print("Interrogatório was updated. Please, open it again.")
            sys.exit()
        if branch:
            repo.git.checkout(branch)
            print("Branch changed to %s. Please open Interrogatório from interrogatorio_for_windows.bat" % branch)
            sys.exit()
    except Exception as e:
        print("Error (Git): {}".format(e))
        sys.exit()


    print("\n=== INTERROGATÓRIO ===\n\n>>> Open 'http://localhost:8000' on your browser to access Interrogatório locally.\nDo not close this window until you have finished using Interrogatório.\n")
    if not 'www' in os.getcwd():
        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "www"))
        server_object = HTTPServer(('', 8000), CGIHTTPRequestHandler)
        webbrowser.open('http://localhost:8000')
        server_object.serve_forever()

main()