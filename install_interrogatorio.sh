if [ ! -d .interrogatorio ]; then
    if ! virtualenv .interrogatorio -p python3; then
        sudo apt update
        sudo apt install virtualenv
        virtualenv .interrogatorio -p python3
    fi
fi

. .interrogatorio/bin/activate
pip3 install --disable-pip-version-check -r requirements.txt
