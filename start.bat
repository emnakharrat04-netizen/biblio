@echo off
REM =============================================================
REM  Bibliothèque Intelligente – Lanceur Windows
REM  Double-cliquez ou exécutez depuis le terminal.
REM =============================================================

REM ── Configuration ─────────────────────────────────────────────
set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=root
set DB_PASSWORD=
set DB_NAME=bibliotheque
set GEMINI_API_KEY=AQ.Ab8RN6Kmme-Za3mHcR5hUb153ztJGwxSDIY49XaQqDjklvOpMw

REM ── Install deps ──────────────────────────────────────────────
echo [1/3] Installation des dependances Python...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERREUR] pip install a echoue. Verifiez votre installation Python.
    pause & exit /b 1
)

REM ── Start backend in a new window ─────────────────────────────
echo [2/3] Demarrage du backend FastAPI...
start "Backend - Bibliotheque" cmd /k "cd backend && python main.py"

REM Wait a moment for the server to bind
timeout /t 3 /nobreak >nul

REM ── Start frontend ────────────────────────────────────────────
echo [3/3] Lancement de l'interface graphique...
cd frontend
python app.py

echo.
echo Application fermee. Fermez aussi la fenetre Backend si necessaire.
pause
