## Setup Instructions

1. **Clone the repository** (if applicable):
   ```bash
   git clone https://github.com/Bashlenix/VitalTrack.git
   cd VitalTrack
   ```

2. **Create and activate a Python virtual environment**:
   
   On macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   On Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up email configuration**:
   
   The application requires email configuration for account confirmation and password reset functionality. See the `EMAIL_SETUP_GUID.md` file in the codebase for detailed email setup instructions.

5. **Create a `.env` file**:
   
   Copy the example environment file and configure it with your settings:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file and configure the following required variables:
   - `SQLALCHEMY_DATABASE_URI`: MySQL database connection string (format: `mysql+mysqlconnector://username:password@localhost/database_name`)
   - `SECRET_KEY`: A secret key for Flask sessions (using the script below).
   - `SECURITY_PASSWORD_SALT`: A salt for password reset tokens (using the script below).
     - Run **`generate_secrets.py`** to generate a random string for `SECRET_KEY` and `SECURITY_PASSWORD_SALT`:

       ```bash
       python3 scripts/generate_secrets.py
        ```

   - `MAIL_SERVER`: SMTP server address (e.g., `smtp.gmail.com`)
   - `MAIL_PORT`: SMTP server port (e.g., `587`)
   - `MAIL_USE_TLS`: Set to `True` or `False` depending on your email provider
   - `MAIL_USERNAME`: Your email address
   - `MAIL_PASSWORD`: Your email password or app-specific password
   - `MAIL_DEFAULT_SENDER`: Email address to use as sender (usually same as MAIL_USERNAME)

6. **Set up MySQL database**:
   
   Ensure MySQL is installed and running on your system. Then create a new database for the application:
   ```bash
   mysql -u root -p
   ```
   
   In the MySQL prompt:
   ```sql
   CREATE DATABASE ehr_system;
   EXIT;
   ```
   
   Replace `ehr_system` with your preferred database name, and update the `SQLALCHEMY_DATABASE_URI` in your `.env` file accordingly.

7. **Initialize the database**:
   
   Run the database initialization script to create all required tables:
   ```bash
   python3 scripts/init_db.py
   ```
   
   This script creates all database tables defined in the `models.py` file.

8. **Run the Flask application**:
   
   Start the development server:
   ```bash
   python3 app.py
   ```
   
   Alternatively, you can use:
   ```bash
   flask run
   ```
   
   The application will be available at `http://127.0.0.1:5000` (or `http://localhost:5000`).

9. **Access the application**:
   
   Open your web browser and navigate to `http://127.0.0.1:5000` to access the EHR system. You can register a new doctor account to begin using the system.

**Note**: Make sure MySQL is running before starting the application. If you encounter database connection errors, verify that:
- MySQL service is running
- Database credentials in `.env` are correct
- The database specified in `SQLALCHEMY_DATABASE_URI` exists
