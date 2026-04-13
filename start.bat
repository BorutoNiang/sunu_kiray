@echo off
chcp 65001 >nul
title Sunu Kiray — API

echo.
echo  ╔══════════════════════════════════════╗
echo  ║        SUNU KIRAY — API              ║
echo  ║   Plateforme medicale senegalaise    ║
echo  ╚══════════════════════════════════════╝
echo.

:: Vérifier que Python est disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
    pause
    exit /b 1
)

:: Vérifier que le dossier backend existe
if not exist "backend\main.py" (
    echo [ERREUR] Fichier backend\main.py introuvable.
    echo Assurez-vous de lancer ce script depuis la racine du projet.
    pause
    exit /b 1
)

:: Installer les dépendances si nécessaire
echo [INFO] Verification des dependances...
pip install -r backend\requirements.txt -q

echo.
echo [OK] Demarrage de l'API sur http://localhost:8001
echo [OK] Frontend : http://localhost:8001/app/auth.html
echo [OK] Documentation API : http://localhost:8001/docs
echo [OK] Appuyez sur CTRL+C pour arreter
echo.

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
