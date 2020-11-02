@ECHO OFF
ubuntu run exit && (
  del /f C:\Interrogatorio_ini >nul 2>&1
  if exist Interrogat-rio (
    start "" ubuntu run LANG="en_US.UTF-8"; cd Interrogat-rio; sh run_interrogatorio.sh
    ping 127.0.0.1 -n 10 > nul
    start "" http://localhost:8000
    exit
  ) else ( 
    start "" ubuntu run "git clone https://github.com/alvelvis/Interrogat-rio; cd Interrogat-rio; sh install_interrogatorio.sh"
    exit
  )
)||(
  if exist C:\Interrogatorio_ini (
    start "" https://www.microsoft.com/pt-br/p/ubuntu/9nblggh4msv6
    exit
  ) else (
    net session >nul 2>&1 && (
      powershell -Command "dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart"
      echo WSL enabled> C:\Interrogatorio_ini
      echo Computer rebooting in a few seconds...
      shutdown /r
    )||(
      ECHO Run this as administrator for the first time.
    )
  )
)
pause
