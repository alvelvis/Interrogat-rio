@ECHO OFF
ubuntu run exit >nul 2>&1 && (
    if exist Interrogat-rio (
      del /f Interrogatorio_ini
      start "" ubuntu run LANG="en_US.UTF-8"; cd Interrogat-rio; sh run_interrogatorio.sh
      start "" http://localhost:8000
      exit
    ) else ( 
      ubuntu run "git clone https://github.com/alvelvis/Interrogat-rio"
      ubuntu run "cd Interrogat-rio; sh install_interrogatorio.sh"
      start "" ubuntu run LANG="en_US.UTF-8"; cd Interrogat-rio; sh run_interrogatorio.sh
      start "" http://localhost:8000
      exit
    )
) || (
    if exist Interrogatorio_ini (
      start "" https://www.microsoft.com/pt-br/p/ubuntu/9nblggh4msv6
      exit
    ) else (
      powershell -Command "dism.exe -Verb RunAs -ArgumentList '/online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart /c'"
      echo WSL enabled> Interrogatorio_ini
      shutdown /r /t 30
    )
)
pause