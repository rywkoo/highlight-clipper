@echo off
:: Batch file to update Git repo and overwrite local changes

echo Updating repository in: %cd%
echo.

:: Check if this is a git repository
git rev-parse --is-inside-work-tree >nul 2>&1
if not "%ERRORLEVEL%" == "0" (
    echo This is not a Git repository.
    echo Make sure you are inside a valid repo folder.
    echo.
    pause
    exit /b
)

echo Discarding local changes...
git reset
git checkout -- .

echo Pulling latest changes from origin/main...
git pull origin main

if "%ERRORLEVEL%" == "0" (
    echo Update completed successfully.
) else (
    echo Error occurred during update.
)

echo.
pause
