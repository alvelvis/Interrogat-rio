if [ ! -d .interrogatorio ]; then
    if ! virtualenv .interrogatorio -p python3; then
        sudo apt update
        sudo apt install virtualenv
        virtualenv .interrogatorio -p python3
    fi
fi

. .interrogatorio/bin/activate
.interrogatorio/bin/pip3 install -r requirements.txt
