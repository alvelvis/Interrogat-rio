@ECHO OFF
if exist Python39\ (
    echo 
    Python39\Python.exe for_windows.py stable
) else (
    echo Python39 not found, please download the Windows release from https://github.com/alvelvis/Interrogat-rio and extract the folder from the zip file.
)
pause