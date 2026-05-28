from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def readBatchFile(name):
    return (REPO_ROOT / "src" / name).read_text(encoding="utf-8")


def testStartBatchUsesSrcRelativeBackendAndFrontendCommands():
    script = readBatchFile("start.bat")

    assert 'set "SCRIPT_DIR=%~dp0"' in script
    assert 'set "BACKEND_DIR=%SCRIPT_DIR%backend"' in script
    assert 'set "FRONTEND_DIR=%SCRIPT_DIR%frontend"' in script
    assert 'start "Market Dashboard Backend" /D "%BACKEND_DIR%" cmd /k "uvicorn main:app --host 127.0.0.1 --port 8000"' in script
    assert 'start "Market Dashboard Frontend" /D "%FRONTEND_DIR%" cmd /k "npm run dev"' in script


def testStopBatchTerminatesConfiguredLocalPorts():
    script = readBatchFile("stop.bat")

    assert 'call :stopPort 8000 "backend"' in script
    assert 'call :stopPort 5173 "frontend"' in script
    assert 'netstat -aon ^| findstr /r /c:":%PORT% .*LISTENING"' in script
    assert "taskkill /f /pid %%P" in script
