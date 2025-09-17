# TaskFlow Project

## MySQL Configuration

### Setting up MySQL Database

1. **Using Docker Compose (Recommended)**

   The project includes a `docker-compose.yml` file for easy local development:

   ```bash
   docker-compose up -d
   ```

   This will start MySQL, Redis, and the Django application.

2. **Manual MySQL Setup**

   If you prefer to set up MySQL manually:

   - Create a new MySQL database:
     ```sql
     CREATE DATABASE taskflow;
     CREATE USER 'taskflow_user'@'%' IDENTIFIED BY 'password';
     GRANT ALL PRIVILEGES ON taskflow.* TO 'taskflow_user'@'%';
     FLUSH PRIVILEGES;
     ```

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp django_backend/.env.example django_backend/.env
   ```

2. Update the `.env` file with your MySQL credentials:
   ```
   USE_SQLITE=false
   MYSQL_DATABASE=taskflow
   MYSQL_USER=your_mysql_user
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_HOST=127.0.0.1
   MYSQL_PORT=3306
   ```

### Running Migrations

Navigate to the Django backend directory and run:

```bash
cd django_backend
python manage.py makemigrations
python manage.py migrate
```

### Development Mode

For local development without Docker, you can still use SQLite by setting:
```
USE_SQLITE=true
```

This is useful for CI environments or quick local testing.