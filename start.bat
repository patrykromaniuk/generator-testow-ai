@echo off
echo ==================================================
echo    URUCHAMIANIE SYSTEMU GENERATORA TESTOW AI
echo ==================================================
echo.

echo 1. Uruchamianie Backend API (FastAPI)...
start "Backend API (Nie zamykaj!)" cmd /k ".\venv\Scripts\activate && uvicorn api:app --reload"

echo 2. Czekanie 5 sekund na start serwera...
timeout /t 5 >nul

echo 3. Uruchamianie Frontend (Streamlit)...
start "Frontend (Nie zamykaj!)" cmd /k ".\venv\Scripts\activate && streamlit run app.py"

echo.
echo ==================================================
echo    GOTOWE! SYSTEM DZIALA W DWOCH OKNACH.
echo ==================================================
echo Mozesz zminimalizowac te okna, ale ich NIE ZAMYKAJ.
pause