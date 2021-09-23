@ECHO OFF
if not exist ".interrogatorio_for_windows" (
    virtualenv .interrogatorio_for_windows
    .interrogatorio_for_windows\Scripts\pip.exe install -r requirements.txt
)
.interrogatorio_for_windows\Scripts\python.exe interrogatorio_for_windows.py
pause