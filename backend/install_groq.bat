@echo off
echo ========================================
echo   Installing Groq for AI Email Assistant
echo ========================================
echo.

echo [1/2] Installing langchain-groq...
pip install langchain-groq

echo.
echo [2/2] Verifying installation...
python -c "import langchain_groq; print('✓ langchain-groq installed successfully')" 2>nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ✓ Installation Complete!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Make sure GROQ_API_KEY is set in .env file
    echo 2. Start the server: uvicorn app.main:app --reload
    echo.
) else (
    echo.
    echo ========================================
    echo   ✗ Installation Failed
    echo ========================================
    echo.
    echo Please try: pip install langchain-groq
    echo.
)

pause
