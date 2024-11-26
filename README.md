# Shoe Inventory Management System

The Shoe Inventory Management System is a web-based program that enables shoe shops to manage their inventory more efficiently. The system tracks stock levels, monitors sales, updates inventory in real time, and generates reports on sales patterns and inventory status. Its goal is to streamline inventory procedures, decrease errors, and improve decision-making about stock replenishment and product availability.

---

## How to Install or Use the Project

### Prerequisites
Before starting, ensure you have the following installed on your machine:
- Python 3.8 or later
- Pip (Python package manager)
- Git (to clone the repository)
- Virtualenv

### Installation Steps

#### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd <repository-url>


python -m venv venv
venv\\Scripts\\activate       # On Windows


pip install -r requirements.txt


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


python manage.py makemigrations
python manage.py migrate


python manage.py createsuperuser


python manage.py runserver


