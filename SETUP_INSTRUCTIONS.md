# UdemyTestMaker Django App Setup Instructions

## Prerequisites
- Python 3.11 or higher
- Poetry (for dependency management)
- PostgreSQL database
- Node.js (for Tailwind CSS)

## Step-by-Step Setup

### 1. Initialize the Poetry Project
```bash
# Create project directory
mkdir udemy-test-maker
cd udemy-test-maker

# Copy the pyproject.toml file to this directory
# Then install dependencies
poetry install
```

### 2. Activate Poetry Shell
```bash
poetry shell
```

### 3. Create Django Project Structure
```bash
# Create the main Django project
django-admin startproject udemy_test_maker .

# Create the tests_app
python manage.py startapp tests_app
```

### 4. Replace Generated Files
Replace the auto-generated files with the ones provided:
- `udemy_test_maker/settings.py`
- `udemy_test_maker/urls.py`
- `udemy_test_maker/wsgi.py`
- `udemy_test_maker/asgi.py`
- `tests_app/apps.py`
- `tests_app/urls.py`
- `tests_app/views.py`

### 5. Setup Environment Variables
1. Copy the `.env` file to your project root
2. Update the database credentials and secret key as needed

### 6. Setup PostgreSQL Database
```bash
# Create PostgreSQL database (adjust credentials as needed)
createdb udemy_test_maker

# Or using psql
psql -U postgres
CREATE DATABASE udemy_test_maker;
\q
```

### 7. Initialize Tailwind CSS
```bash
# Install Tailwind
python manage.py tailwind install

# Start Tailwind in development mode (run in separate terminal)
python manage.py tailwind start
```

### 8. Run Django Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 9. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 10. Create Required Directories
```bash
mkdir -p static templates/tests_app
```

### 11. Run Development Server
```bash
python manage.py runserver
```

## Next Steps

After completing the setup, you can proceed with:
1. **Database Models** - Define Question, Answer, Exam, and Domain models
2. **Templates** - Create HTML templates with Tailwind CSS
3. **Forms** - Build forms for adding questions and answers
4. **CSV Generation** - Implement CSV export functionality

## Troubleshooting

### Common Issues:

1. **PostgreSQL Connection Error**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env` file
   - Verify database exists

2. **Tailwind CSS Not Working**
   - Ensure Node.js is installed
   - Run `python manage.py tailwind install`
   - Start Tailwind with `python manage.py tailwind start`

3. **Import Errors**
   - Ensure you're in the Poetry shell: `poetry shell`
   - Check if all dependencies are installed: `poetry install`

4. **Static Files Issues**
   - Run `python manage.py collectstatic` for production
   - Ensure static directories exist

## Development Workflow

1. Always activate Poetry shell: `poetry shell`
2. Run Tailwind in development: `python manage.py tailwind start`
3. Run Django server: `python manage.py runserver`
4. Make migrations after model changes: `python manage.py makemigrations && python manage.py migrate`