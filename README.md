# Restaurant–Customer Platform (Django + DRF)

Marketing site, partners portal, and full REST API for multi-phase loyalty/payment platform. React Native app consumes the API.

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

Open `http://127.0.0.1:8000/` (marketing), `http://127.0.0.1:8000/admin/` (admin), docs at `http://127.0.0.1:8000/api/docs/`.

## API Overview

- Auth: JWT, registration, RBAC (Admin/BusinessOwner/Customer)
- Businesses, Campaigns, QR Codes
- Rewards (points history/balance, QR scan validate/award, redeem)
- Reviews (submit/list)
- Notifications (FCM register, send test)
- Payments (Stripe PaymentIntent, webhook, orders)
- Analytics (event ingest, admin list)
- Security (audit logging, GDPR export/delete, optional field encryption)

### Key Endpoints

- Accounts: `POST /api/accounts/register/`, `POST /api/accounts/token/`, `GET /api/accounts/me/`
- Campaigns: `GET /api/campaigns/public/`, `GET/POST /api/campaigns/`, `GET/PATCH /api/campaigns/{id}/`
- QR: `POST /api/qr/`, `GET /api/qr/image/{token}.png`, `POST /api/qr/validate/`
- Rewards: `GET /api/rewards/history/`, `GET /api/rewards/balance/`, `POST /api/rewards/scan/`, `POST /api/rewards/redeem/`
- Reviews: `GET/POST /api/reviews/?business_id=...`
- Payments: `GET /api/payments/orders/`, `POST /api/payments/initiate/`, `POST /api/payments/stripe/webhook/`
- Analytics: `POST /api/analytics/ingest/`, `GET /api/analytics/events/`
- Notifications: `POST /api/notifications/register-device/`, `POST /api/notifications/send-test/`
- Security: `GET /api/security/gdpr/export/`, `POST /api/security/gdpr/delete/`

