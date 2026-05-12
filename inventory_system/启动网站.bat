@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "VENV_PY=%CD%\.venv\Scripts\python.exe"
set "VENV_PIP=%CD%\.venv\Scripts\pip.exe"

if not exist "%VENV_PY%" (
  echo [错误] 未找到虚拟环境：%VENV_PY%
  echo.
  echo 请在本文件夹地址栏输入 cmd 回车，然后依次执行：
  echo   python -m venv .venv
  echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
  echo   .venv\Scripts\python.exe -m flask --app app init-db
  echo 完成后可再双击本 bat。
  pause
  exit /b 1
)

"%VENV_PY%" -c "import flask" 2>nul
if errorlevel 1 (
  echo [提示] 虚拟环境里还没有 Flask，正在安装 requirements.txt ...
  "%VENV_PY%" -m pip install -r "%CD%\requirements.txt"
  if errorlevel 1 (
    echo [错误] pip 安装失败，请检查网络或 Python 是否可用。
    pause
    exit /b 1
  )
)

echo 正在启动 http://127.0.0.1:5000 ...
echo 使用的是："%VENV_PY%"
echo 关闭本窗口即停止网站。
"%VENV_PY%" "%CD%\app.py"
pause
