# Sancta Maria Agency – Savings Manager (Django)

    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createowner you@email.com YourStrongPassword
    python manage.py runserver

- Owner: http://127.0.0.1:8000/owner/login/ (email + password)
- Customer: http://127.0.0.1:8000/login/ (name, case-insensitive + card number)
Owner adds customers, records deposits by date, and views daily/monthly/yearly statements.
