# Quick Campus Feedback – Account Feature (Project Development 1)

Django 6.1 (templates) + PostgreSQL / Supabase.

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate            # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # Mac/Linux: cp .env.example .env  -> then fill in your database details
python manage.py migrate
python manage.py createsuperuser  # this account becomes the Administrator
python manage.py runserver
```

## Features
- Sign up (`/accounts/signup/`): required fields, school-email check, unique username and email, password confirmation, hashed passwords
- Log in / log out (`/accounts/login/`, logout is a POST button)
- Role dashboards: Student (`/student/`) and Administrator (`/admin-panel/`); `/` redirects by role
- Profile (`/accounts/profile/`, `/accounts/profile/edit/`): own profile only

Run the tests with `python manage.py test` (they need a database your user can create test databases in).
