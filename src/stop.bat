@echo off
setlocal

call :stopPort 8000 "backend"
call :stopPort 5173 "frontend"

echo Done.
exit /b 0

:stopPort
set "PORT=%~1"
set "LABEL=%~2"
set "FOUND="

echo Looking for %LABEL% process on port %PORT% ...

for /f "tokens=5" %%P in ('netstat -aon ^| findstr /r /c:":%PORT% .*LISTENING"') do (
    set "FOUND=1"
    echo Stopping PID %%P on port %PORT% ...
    taskkill /f /pid %%P
)

if not defined FOUND (
    echo No process is listening on port %PORT%.
)

exit /b 0
