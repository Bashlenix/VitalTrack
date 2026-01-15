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

---

## Docker Setup (Alternative Installation Method)

This project is containerized using Docker and Docker Compose, making it easy to run the entire application stack with a single command.

### Prerequisites

- [Docker](https://www.docker.com/get-started) (version 20.10 or later)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0 or later)

### Quick Start with Docker

1. **Ensure you have a `.env` file**:
   
   The `.env` file should contain all required environment variables. The Docker setup will automatically use the database service name `db` instead of `localhost` when running in containers.

   **Important**: For Docker, you don't need to set `SQLALCHEMY_DATABASE_URI` in your `.env` file. Instead, the following variables will be used to construct the connection string:
   - `MYSQL_DATABASE`: Database name (default: `vitaltrack`)
   - `MYSQL_USER`: Database user (default: `vitaltrack_user`)
   - `MYSQL_PASSWORD`: Database password (default: `vitaltrack_password`)
   - `MYSQL_ROOT_PASSWORD`: MySQL root password (default: `rootpassword`)

   You can also set these in your `.env` file, or they will use the defaults specified in `docker-compose.yml`.

   **Database Initialization**: The MySQL container automatically initializes the database from `./db/init.sql` on first run. The SQL dump will be executed in the database specified by `MYSQL_DATABASE`. Ensure the database name in your environment variables matches what your application expects.

   Your `.env` file should still contain:
   - `SECRET_KEY`: Flask secret key
   - `SECURITY_PASSWORD_SALT`: Password reset salt
   - Email configuration variables (`MAIL_SERVER`, `MAIL_PORT`, etc.)

2. **Build and start the containers**:
   ```bash
   docker-compose up --build
   ```
   
   This command will:
   - Build the Flask application Docker image
   - Start the MySQL database container
   - **Automatically initialize the database** from `./db/init.sql` on first run
   - Start the Flask web application container
   - Wait for MySQL to be ready before starting Flask

   **Note**: The MySQL container automatically executes the SQL dump file (`./db/init.sql`) on first initialization. This happens when the data directory is empty, so you don't need to manually run database initialization scripts.

3. **Access the application**:
   
   Open your web browser and navigate to `http://localhost:5001` to access the EHR system.
   
   **Note**: The Flask application is exposed on host port **5001** (mapped to container port 5000).

### Docker Commands Reference

- **Start containers in detached mode** (background):
  ```bash
  docker-compose up -d
  ```

- **View container logs**:
  ```bash
  docker-compose logs -f
  ```

- **Stop containers**:
  ```bash
  docker-compose down
  ```

- **Stop containers and remove volumes** (⚠️ This will delete all data):
  ```bash
  docker-compose down -v
  ```

- **Rebuild containers after code changes**:
  ```bash
  docker-compose up --build
  ```

- **Execute commands in the Flask container**:
  ```bash
  docker-compose exec web <command>
  ```

### Data Persistence

- **MySQL Data**: Stored in a Docker volume named `mysql_data`. This persists even if containers are stopped.
- **Uploaded Files**: The `static/uploads/` directory is mounted as a volume, so uploaded files persist on your host machine.

### Troubleshooting Docker Setup

1. **Port conflicts**:
   - Flask application uses host port **5001** (change `"5001:5000"` in `docker-compose.yml` if needed)
   - MySQL uses host port **3307** (change `"3307:3306"` in `docker-compose.yml` if needed)
   - Update the `HOST_PORT` environment variable in `docker-compose.yml` to match the host port if you change it

2. **Database connection errors**:
   - Ensure the `db` service is healthy before Flask starts (health checks are configured)
   - Verify MySQL credentials in your `.env` file match those in `docker-compose.yml`

3. **Permission errors with uploads**:
   - Ensure the `static/uploads/` directory exists and has proper permissions
   - The Docker container will create the directory structure if needed

4. **View container status**:
   ```bash
   docker-compose ps
   ```