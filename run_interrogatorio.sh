if [ ! -e www ]; then
  sudo ln -rs www/interrogar-ud/ .; sudo ln -rs www/cgi-bin/ .; sudo chmod -R a+rwx www
fi

if [ -d .git ]; then
  git update-index --assume-unchanged www/cgi-bin/credenciar.py
fi

cd www; python3 -m http.server --cgi; cd ..

