@echo off
title Documents NETUBEX SARL
cd /d "%~dp0"
echo Demarrage de l'application...
echo.
streamlit run app.py --server.headless false --server.port 8510 --browser.gatherUsageStats false
pause