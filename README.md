# Manidham Trust Platform

A full-stack NGO platform for **Manidham Trust**, connecting communities through three core initiatives:

- **Education** for underprivileged children
- **Direct blood donation** from donors to patients
- **Food waste redistribution** from hotels to orphanages and old age homes

## Tech Stack

- **Backend:** Python Flask + SQLAlchemy + SQLite (auto-initialized)
- **Frontend:** React + Vite + Framer Motion
- **Database:** SQLite (`backend/instance/manidham.db`)

## Features

- Donor enrollment with international donor support
- Donor search by city, district, and blood group
- Urgent blood request system with automatic donor notifications
- Restaurant/hotel enrollment and surplus food logging
- Orphanage and old age home enrollment
- Automatic area-based notifications for food and blood requests
- Admin dashboard with platform statistics and records

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

The API runs at `http://127.0.0.1:5000`. The SQLite database is created automatically on first run with sample seed data.

### 2. Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173` in your browser. The Vite dev server proxies `/api` requests to the Flask backend.

## Images

All photography is stored locally in `frontend/public/images/` and referenced through
`frontend/src/constants/images.js`. Nothing is hotlinked, so images cannot break due to an
external host going away, and they are copied into `dist/` automatically on build.

## Verifying the Backend

With `app.py` running, you can exercise every endpoint and the notification matching logic:

```bash
cd backend
venv\Scripts\python smoke_test.py     # Windows
```

This creates a few test records. To remove them again:

```bash
venv\Scripts\python clear_test_data.py
```

To check the validation and privacy rules specifically, run the regression script. It
cleans up after itself, so it is safe to re-run:

```bash
venv\Scripts\python validation_checks.py
```

## Donor Privacy

Donor phone numbers, email addresses, dates of birth and exact ages are **never** returned
by the public search endpoint, and surnames are abbreviated (`Arun K.`). Searching shows
only that a matching donor exists; to reach them, a requester submits a blood request and
every matching donor is notified with the requester's contact details. This keeps the donor
list from being scraped as a contact database.

Notification text can contain patient phone numbers, so it is only served from the `/api/admin/*`
routes. **Those routes are still unauthenticated — add admin authentication before deploying
publicly.**

## Validation Rules

Enforced server-side, so they hold regardless of what the client sends:

- Email addresses must be well-formed; phone numbers need at least 8 digits
- Donors must be between 18 and 65, and the submitted age must agree with the date of birth
- Dates of birth cannot be in the future
- Blood groups must be one of the eight valid groups
- A donor's email or phone may only be enrolled once (`409` on duplicates)
- Blood request urgency must be `routine`, `urgent` or `critical`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/donors` | Enroll a blood donor |
| GET | `/api/donors/search` | Search donors by area and blood group (no contact details) |
| POST | `/api/restaurants` | Enroll a restaurant/hotel |
| POST | `/api/institutions` | Enroll an orphanage or old age home |
| POST | `/api/food-log` | Log surplus food and notify institutions |
| POST | `/api/blood-requests` | Create urgent blood request and notify donors |
| GET | `/api/admin/stats` | Platform statistics |
| GET | `/api/admin/*` | Admin data views |
| POST | `/api/admin/notifications/<id>/read` | Mark a notification as read |

## Production Build

```bash
cd frontend
npm run build
```

Serve the built files from Flask or any static host, ensuring API routes proxy to the backend.

## Project Structure

```
manidham/
├── backend/
│   ├── app.py                # Flask API and notification logic
│   ├── models.py             # SQLAlchemy models
│   ├── smoke_test.py         # End-to-end API check
│   ├── validation_checks.py  # Validation and privacy regression checks
│   ├── clear_test_data.py    # Removes smoke test records
│   ├── requirements.txt
│   └── instance/             # SQLite database (auto-created)
└── frontend/
    ├── public/images/        # All site photography
    ├── src/
    │   ├── components/       # React UI components
    │   ├── api.js            # API client
    │   └── constants/        # Image paths and constants
    └── vite.config.js        # Dev proxy to backend
```

## License

Built for Manidham Trust — for community impact and humanitarian service.
