@ECHO OFF
if exist Python39\ (
    Python39\Python.exe for_windows.py
) else (
    echo Python39 not found, please download the Windows release from https://github.com/alvelvis/Interrogat-rio and extract the folder from the zip file.
)
pause