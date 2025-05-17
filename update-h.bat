@echo off
:: Batch file to force update Git repo, overwriting all local changes

echo.
echo Updating repository in: %cd%
echo.

:: Check if this is a git repo
git rev-parse --is-inside-work-tree >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo This is not a Git repository!
    echo.
    echo Please run this script inside a valid Git repository folder.
    echo.
    pause
    exit /b
)

:: Reset and remove all local changes
echo Discarding all local changes...
git reset
git checkout -- .

:: Pull latest code from origin/main
echo.
echo Pulling latest changes from origin/main...
git pull origin main

:: Check result
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Repository updated successfully!
) else (
    echo.
    echo Error occurred while updating the repository.
)

echo.
pause