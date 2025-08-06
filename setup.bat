@echo off
echo Setting up FastAPI Authentication System...

echo.
echo 1. Installing Python dependencies...
pip install -r requirements.txt

echo.
echo 2. Setting up environment variables...
echo Please make sure to update the .env file with your database and email configuration

echo.
echo 3. Database setup instructions:
echo    - Create a PostgreSQL database
echo    - Update DATABASE_URL in .env file
echo    - Run: alembic revision --autogenerate -m "Initial migration"
echo    - Run: alembic upgrade head

echo.
echo 4. To start the application:
echo    python main.py
echo    or
echo    uvicorn main:app --reload

echo.
echo 5. Access the application at: http://localhost:8000

echo.
echo Super Admin credentials:
echo Email: superadmin@company.com
echo Password: SuperSecurePassword123!

pause
