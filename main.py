"""
Apollo Hospitals — FastAPI Backend with SQLite Database
=========================================================
Run karne ke liye:
  pip install fastapi uvicorn[standard]
  uvicorn main:app --reload

API available at: http://localhost:8000
Docs available at: http://localhost:8000/docs
Database file:    apollo.db  (automatically ban jaayegi)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import sqlite3
import os

# ─── App Setup ───────────────────────────────────────────────
app = FastAPI(title="Apollo Hospitals API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Database Setup ──────────────────────────────────────────
DB_FILE = "apollo.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id          TEXT PRIMARY KEY,
            full_name   TEXT NOT NULL,
            phone       TEXT NOT NULL,
            department  TEXT NOT NULL,
            date        TEXT,
            time        TEXT,
            notes       TEXT,
            status      TEXT DEFAULT 'confirmed',
            created_at  TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            specialty       TEXT NOT NULL,
            qualifications  TEXT,
            experience      TEXT,
            available       INTEGER DEFAULT 1,
            image           TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            icon        TEXT,
            description TEXT,
            services    TEXT
        )
    """)

    _seed_data(cursor)
    conn.commit()
    conn.close()
    print("✅ Database ready:", os.path.abspath(DB_FILE))


def _seed_data(cursor):
    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] > 0:
        return

    print("🌱 Seed data inserting...")

    doctors = [
        ("Dr. Sarah Mitchell",   "cardiologist",    "MD, FACC, FSCAI",       "15 years", 1,
         "https://images.pexels.com/photos/5327585/pexels-photo-5327585.jpeg?auto=compress&cs=tinysrgb&w=400&h=500&fit=crop"),
        ("Dr. James Chen",       "neurologist",     "MD, PhD, FAAN",         "20 years", 1,
         "https://images.pexels.com/photos/5452201/pexels-photo-5452201.jpeg?auto=compress&cs=tinysrgb&w=400&h=500&fit=crop"),
        ("Dr. Emily Rodriguez",  "pediatrician",    "MD, FAAP",              "10 years", 1,
         "https://images.pexels.com/photos/5214958/pexels-photo-5214958.jpeg?auto=compress&cs=tinysrgb&w=400&h=500&fit=crop"),
        ("Dr. Michael Thompson", "orthopedics",     "MD, FAAOS",             "18 years", 1,
         "https://images.pexels.com/photos/4173251/pexels-photo-4173251.jpeg?auto=compress&cs=tinysrgb&w=400&h=500&fit=crop"),
        ("Dr. Priya Sharma",     "dermatologist",   "MD, DNB Dermatology",   "12 years", 1,
         "https://images.pexels.com/photos/5407206/pexels-photo-5407206.jpeg?auto=compress&cs=tinysrgb&w=400&h=500&fit=crop"),
        ("Dr. Rajesh Kumar",     "ophthalmologist", "MS Ophthalmology, FRCS","22 years", 0,
         "https://images.pexels.com/photos/5215024/pexels-photo-5215024.jpeg?auto=compress&cs=tinysrgb&w=400&h=500&fit=crop"),
    ]
    cursor.executemany(
        "INSERT INTO doctors (name, specialty, qualifications, experience, available, image) VALUES (?,?,?,?,?,?)",
        doctors
    )

    departments = [
        ("cardiology",    "Cardiology",    "favorite",
         "Comprehensive heart care with cutting-edge diagnostic and treatment options.",
         "Heart Valve Repair,Angioplasty,Pacemaker Implantation,Echo-Cardiography"),
        ("neurology",     "Neurology",     "psychology",
         "Expert care for disorders of the nervous system using advanced imaging tools.",
         "Stroke Management,Epilepsy Care,Sleep Disorders,Dementia Care"),
        ("orthopedics",   "Orthopedics",   "accessibility_new",
         "Bone, joint, and muscle treatment from joint replacements to sports medicine.",
         "Joint Replacement,Arthroscopy,Spine Surgery,Sports Injury Rehab"),
        ("pediatrics",    "Pediatrics",    "child_care",
         "Compassionate healthcare for infants, children, and adolescents.",
         "Vaccinations,Growth Monitoring,Neonatal Intensive Care,Childhood Infections"),
        ("dermatology",   "Dermatology",   "face",
         "Advanced skin, hair, and nail treatments using latest dermatological technology.",
         "Acne Treatment,Skin Cancer Screening,Laser Therapy,Hair Transplant"),
        ("ophthalmology", "Ophthalmology", "visibility",
         "Complete eye care from routine check-ups to advanced surgical procedures.",
         "Cataract Surgery,LASIK,Glaucoma Treatment,Retinal Disorders"),
    ]
    cursor.executemany(
        "INSERT INTO departments (id, name, icon, description, services) VALUES (?,?,?,?,?)",
        departments
    )
    print("✅ Seed data inserted!")


# ─── Static Data ─────────────────────────────────────────────
STATS = {
    "expert_doctors": 500,
    "departments": 50,
    "happy_patients": "1M+",
    "emergency": "24/7",
    "years_of_service": 25,
}

FAQS = [
    {"question": "How do I book an appointment?",
     "answer": "Book through our website form or call 1800 123 4567. Same-day appointments available."},
    {"question": "What insurance plans do you accept?",
     "answer": "We accept Apollo Munich, ICICI Lombard, HDFC ERGO, Star Health, and most major providers."},
    {"question": "Do you have emergency services?",
     "answer": "Yes — 24/7 emergency and trauma services with specialized doctors and ambulances."},
    {"question": "Can I get an online consultation?",
     "answer": "Yes! Book a video consultation through the website by selecting Online mode."},
    {"question": "What are your visiting hours?",
     "answer": "General visiting: 9 AM to 8 PM. ICU: 10 AM to 12 PM and 5 PM to 7 PM (max 2 visitors)."},
]


# ─── Pydantic Models ─────────────────────────────────────────
class AppointmentRequest(BaseModel):
    full_name: str
    phone: str
    department: str
    date: Optional[str] = None
    time: Optional[str] = None
    notes: Optional[str] = None


# ─── Routes ──────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "message": "Apollo Hospitals API is running",
        "database": os.path.abspath(DB_FILE),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stats", tags=["General"])
def get_stats():
    return STATS

@app.get("/faqs", tags=["General"])
def get_faqs():
    return FAQS

@app.get("/departments", tags=["Departments"])
def get_departments():
    conn = get_db()
    rows = conn.execute("SELECT * FROM departments").fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["services"] = d["services"].split(",") if d["services"] else []
        result.append(d)
    return result

@app.get("/departments/{dept_id}", tags=["Departments"])
def get_department(dept_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM departments WHERE id=?", (dept_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Department '{dept_id}' not found")
    d = dict(row)
    d["services"] = d["services"].split(",") if d["services"] else []
    return d

@app.get("/doctors", tags=["Doctors"])
def get_doctors(specialty: Optional[str] = None, available: Optional[bool] = None):
    query = "SELECT * FROM doctors WHERE 1=1"
    params = []
    if specialty:
        query += " AND LOWER(specialty) = LOWER(?)"
        params.append(specialty)
    if available is not None:
        query += " AND available = ?"
        params.append(1 if available else 0)
    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["available"] = bool(d["available"])
        result.append(d)
    return result

@app.get("/doctors/{doctor_id}", tags=["Doctors"])
def get_doctor(doctor_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM doctors WHERE id=?", (doctor_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Doctor {doctor_id} not found")
    d = dict(row)
    d["available"] = bool(d["available"])
    return d

@app.post("/appointments", status_code=201, tags=["Appointments"])
def book_appointment(appt: AppointmentRequest):
    if not appt.full_name.strip():
        raise HTTPException(status_code=422, detail="Full name required")
    if not appt.phone.strip():
        raise HTTPException(status_code=422, detail="Phone number required")
    if not appt.department:
        raise HTTPException(status_code=422, detail="Department required")

    conn = get_db()
    dept = conn.execute("SELECT id FROM departments WHERE id=?", (appt.department.lower(),)).fetchone()
    if not dept:
        conn.close()
        raise HTTPException(status_code=422, detail=f"Invalid department: {appt.department}")

    new_id = str(uuid.uuid4())[:8].upper()
    now    = datetime.now().isoformat()

    conn.execute(
        "INSERT INTO appointments (id, full_name, phone, department, date, time, notes, status, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (new_id, appt.full_name.strip(), appt.phone.strip(),
         appt.department.lower(), appt.date, appt.time, appt.notes, "confirmed", now)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM appointments WHERE id=?", (new_id,)).fetchone()
    conn.close()
    print(f"✅ Appointment booked: #{new_id} — {appt.full_name} ({appt.department})")
    return dict(row)

@app.get("/appointments", tags=["Appointments"])
def get_all_appointments():
    conn = get_db()
    rows = conn.execute("SELECT * FROM appointments ORDER BY created_at DESC").fetchall()
    conn.close()
    appointments = [dict(r) for r in rows]
    return {"total": len(appointments), "appointments": appointments}

@app.get("/appointments/{appt_id}", tags=["Appointments"])
def get_appointment(appt_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM appointments WHERE id=?", (appt_id.upper(),)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Appointment {appt_id} not found")
    return dict(row)

@app.delete("/appointments/{appt_id}", tags=["Appointments"])
def cancel_appointment(appt_id: str):
    conn = get_db()
    result = conn.execute("DELETE FROM appointments WHERE id=?", (appt_id.upper(),))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Appointment {appt_id} not found")
    return {"message": f"Appointment {appt_id} cancelled successfully"}


# ─── Startup ─────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()
    print("🚀 Apollo Hospitals API started!")
    print("📖 API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
