@echo off
setlocal
pushd "%~dp0"

if not exist "logs" mkdir "logs"

rem Prefer venv python if present to avoid PATH issues.
set PY=
if exist "venv\\Scripts\\python.exe" set PY=venv\\Scripts\\python.exe
if "%PY%"=="" (
  where python >nul 2>&1 && set PY=python
)
if "%PY%"=="" (
  where py >nul 2>&1 && set PY=py
)
if "%PY%"=="" (
  echo ERROR: Python not found. Install Python or activate venv.
  popd
  exit /b 1
)

rem Each agent writes its own logs so failures don't disappear when a window closes.
start "boss_agent" cmd /c "%PY% agents\\boss_agent.py 1>>logs\\boss_agent.out.log 2>>logs\\boss_agent.err.log"
start "technical_agent" cmd /c "%PY% agents\\technical_agent.py 1>>logs\\technical_agent.out.log 2>>logs\\technical_agent.err.log"
start "whale_agent" cmd /c "%PY% agents\\whale_agent.py 1>>logs\\whale_agent.out.log 2>>logs\\whale_agent.err.log"
start "macro_agent" cmd /c "%PY% agents\\macro_agent.py 1>>logs\\macro_agent.out.log 2>>logs\\macro_agent.err.log"
start "news_agent" cmd /c "%PY% agents\\news_agent.py 1>>logs\\news_agent.out.log 2>>logs\\news_agent.err.log"
start "pinescript_agent" cmd /c "%PY% agents\\pinescript_agent.py 1>>logs\\pinescript_agent.out.log 2>>logs\\pinescript_agent.err.log"
start "watchlist_executor" cmd /c "%PY% agents\\watchlist_executor.py 1>>logs\\watchlist_executor.out.log 2>>logs\\watchlist_executor.err.log"
start "hermes_advisor_agent" cmd /c "%PY% agents\\hermes_advisor_agent.py 1>>logs\\hermes_advisor_agent.out.log 2>>logs\\hermes_advisor_agent.err.log"
start "trade_execution_agent" cmd /c "%PY% agents\\trade_execution_agent.py 1>>logs\\trade_execution_agent.out.log 2>>logs\\trade_execution_agent.err.log"

popd
