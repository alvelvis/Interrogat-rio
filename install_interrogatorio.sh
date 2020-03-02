if [ ! -d .interrogatorio ]; then
    virtualenv .interrogatorio -p python3
fi

. .interrogatorio/bin/activate
pip3 install -r requirements.txt