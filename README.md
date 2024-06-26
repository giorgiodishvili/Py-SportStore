# SportStore

SportStore is a Django-based e-commerce application for sports equipment. This project includes features such as user authentication, product management, cart functionality, and product reviews.

## Features

- User registration and login
- Product listing with search and filter options
- Cart functionality
- Product reviews
- User profile management

## Requirements

- Python 3.6+
- Django 3.2+
- Bootstrap 5

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/giorgiodishvili/Py-SportStore
cd SportStore
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
pip install -r requirements.txt
python manage.py makemigrations SportStore
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
