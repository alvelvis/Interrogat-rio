sudo chmod -R a+rwx www

if [ ! -d .interrogatorio ]; then
  sh install_interrogatorio.sh
fi

. .interrogatorio/bin/activate

if ! python3 -c "import udapi"; then
  if ! pip3 install -r requirements.txt; then
    sudo apt install python3-pip
    pip3 install -r requirements.txt
  fi
fi

if [ -d .git ]; then
  git update-index --assume-unchanged www/cgi-bin/credenciar.py
  git update-index --assume-unchanged www/cgi-bin/variables.py
  git update-index --assume-unchanged www/cgi-bin/max_upload.py
  git submodule update --init
  git pull
fi

cd www
python3 -m http.server --cgi
