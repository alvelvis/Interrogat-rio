@ECHO OFF
ubuntu run exit >nul 2>&1 && (
    if exist Interrogat-rio (
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
    start "" https://www.microsoft.com/pt-br/p/ubuntu/9nblggh4msv6
    exit
)
pause