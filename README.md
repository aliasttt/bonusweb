# Bonus Loyalty (Django + REST API)

German-first marketing site, partner portal, and REST API for QR-based stamp loyalty. React Native app can consume the same API.

## Quickstart (Windows PowerShell)

```powershell
cd C:\Users\DELL\Desktop\bonusweb
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\pip.exe install -r requirements.txt
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/` (marketing), `http://127.0.0.1:8000/admin/` (admin), `http://127.0.0.1:8000/partners/qr/` (QR demo).

## API
- POST `/api/auth/token/` JSON: `{"username","password"}` → `{access,refresh}`
- GET `/api/businesses/`
- GET `/api/products/`
- GET `/api/wallet/` (auth)
- POST `/api/scan/` `{business_id, amount}` (auth)
- POST `/api/redeem/` `{business_id}` (auth)

JWT in header: `Authorization: Bearer <access>`

## i18n
- Default language: German (`de`).
- English translations in `locale/en/LC_MESSAGES/django.po`.

## Notes
- Create some `Business` and `Product` rows in Admin to test.
- The QR generator page encodes the JSON payload for scans; the React Native app should parse QR data and call `/api/scan/`.

