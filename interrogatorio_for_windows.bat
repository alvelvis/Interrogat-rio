@ECHO OFF
if exist Python39\ (
    Python39\Python.exe for_windows.py
) else (
    echo "There are missing files in this Windows release of Interrogatorio."
    echo "1. Please download the Windows release from https://github.com/alvelvis/Interrogat-rio/releases"
    echo "2. Make sure to open Interrogatorio from the file interrogatorio_for_windows only after extracting the zipped downloaded file Interrogat-rio.zip to a folder of your choice."
    echo "Avoid extracting the file to a folder shared in the cloud (Dropbox, Google Drive, etc.), as some of the files may not be synchronized correctly, making it impossible to run the program correctly."
)
pause