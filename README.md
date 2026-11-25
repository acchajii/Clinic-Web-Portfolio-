# CarePoint Clinic Website

A responsive clinic website demo built with Flask, PostgreSQL (Supabase-compatible), HTML, CSS and JavaScript.

## Features
- Clinic homepage, services, doctor profiles and contact section
- Appointment request form
- PostgreSQL appointment storage
- Admin login configured through environment variables
- Admin dashboard to review appointments and update status
- Health-check endpoint at `/health`

## Run locally
1. Install Python 3.10+.
2. Run `pip install -r requirements.txt`.
3. Set `DATABASE_URL`, `SECRET_KEY`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD`.
4. Run `python app.py`.
5. Open `http://127.0.0.1:5000`.

The app creates the `appointments` table automatically when the first appointment is submitted or the admin dashboard is opened? For deployment, initialize the table once by visiting `/health` after setting up the database, then use the SQL below if needed.

## Database setup
Run this in Supabase SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS public.appointments (
  id BIGSERIAL PRIMARY KEY,
  patient_name VARCHAR(120) NOT NULL,
  email VARCHAR(160),
  phone VARCHAR(30) NOT NULL,
  service VARCHAR(120) NOT NULL,
  doctor VARCHAR(120),
  appointment_date DATE NOT NULL,
  appointment_time VARCHAR(30) NOT NULL,
  message TEXT,
  status VARCHAR(30) NOT NULL DEFAULT 'Pending',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Render deployment
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add environment variables: `DATABASE_URL`, `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`.
- Keep Root Directory blank if `app.py` is at the repository root.

## Important
This is a customizable demo, not a certified clinical system. Do not collect medical records, diagnoses, prescriptions, payment details, or other sensitive health information through this demo. Replace sample clinic details before publishing. Use HTTPS and a strong unique admin password. The admin login is basic session-based authentication; add stronger protections and review privacy/security requirements before real-world use.
