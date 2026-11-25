import os
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-before-deployment")

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing. Configure your PostgreSQL connection string.")
    return psycopg2.connect(DATABASE_URL, sslmode="require", connect_timeout=15)

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
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
                )
            """)
        conn.commit()

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/book", methods=["POST"])
def book():
    data = {
        "patient_name": request.form.get("patient_name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "service": request.form.get("service", "").strip(),
        "doctor": request.form.get("doctor", "").strip(),
        "appointment_date": request.form.get("appointment_date", "").strip(),
        "appointment_time": request.form.get("appointment_time", "").strip(),
        "message": request.form.get("message", "").strip()
    }
    if not all(data[k] for k in ("patient_name", "phone", "service", "appointment_date", "appointment_time")):
        flash("Please complete all required fields.", "error")
        return redirect(url_for("home") + "#appointment")
    try:
        datetime.strptime(data["appointment_date"], "%Y-%m-%d")
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO appointments
                    (patient_name, email, phone, service, doctor, appointment_date, appointment_time, message)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, tuple(data.values()))
            conn.commit()
        flash("Your appointment request has been submitted. The clinic will contact you to confirm it.", "success")
    except ValueError:
        flash("Please select a valid appointment date.", "error")
    except Exception:
        app.logger.exception("Appointment submission failed")
        flash("We could not submit your request right now. Please contact the clinic directly.", "error")
    return redirect(url_for("home") + "#appointment")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if ADMIN_PASSWORD and username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        flash("Invalid login details. Check the admin credentials configured by the site owner.", "error")
    return render_template("login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM appointments ORDER BY created_at DESC")
                appointments = cur.fetchall()
        return render_template("admin.html", appointments=appointments)
    except Exception:
        app.logger.exception("Admin dashboard could not load")
        flash("Could not load appointments. Check the database connection.", "error")
        return render_template("admin.html", appointments=[])

@app.route("/admin/status/<int:appointment_id>", methods=["POST"])
@admin_required
def update_status(appointment_id):
    status = request.form.get("status", "")
    if status not in ("Pending", "Confirmed", "Completed", "Cancelled"):
        flash("Invalid appointment status.", "error")
        return redirect(url_for("admin"))
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE appointments SET status=%s WHERE id=%s", (status, appointment_id))
            conn.commit()
        flash("Appointment status updated.", "success")
    except Exception:
        app.logger.exception("Status update failed")
        flash("Could not update the appointment.", "error")
    return redirect(url_for("admin"))

@app.route("/health")
def health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}, 200
    except Exception:
        return {"status": "error", "database": "unavailable"}, 503

if __name__ == "__main__":
    if os.getenv("DATABASE_URL"):
        init_db()
    app.run(debug=True)
