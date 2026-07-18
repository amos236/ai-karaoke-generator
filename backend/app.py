from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import os
import shutil
import uuid
import threading

from database import engine, SessionLocal
from models import Base, User, History

from auth import router as auth_router
from login import router as login_router
from profile import router as profile_router
from payment import router as payment_router
from admin import router as admin_router

from services.demucs_service import convert_to_karaoke


# ==========================================
# Create Database
# ==========================================

Base.metadata.create_all(bind=engine)


# ==========================================
# FastAPI
# ==========================================

app = FastAPI(
    title="AI Karaoke Generator",
    version="2.0"
)


# ==========================================
# Routers
# ==========================================

app.include_router(auth_router)
app.include_router(login_router)
app.include_router(profile_router)
app.include_router(payment_router)
app.include_router(admin_router)


# ==========================================
# Folders
# ==========================================

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "ai_output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ==========================================
# Static Files
# ==========================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ==========================================
# HTML Pages
# ==========================================
# ==========================================
# HTML Pages
# ==========================================

@app.get("/")
async def home():
    return FileResponse("templates/index.html")


@app.get("/index.html")
async def home_html():
    return FileResponse("templates/index.html")


@app.get("/login")
async def login_page():
    return FileResponse("templates/login.html")


@app.get("/register")
async def register_page():
    return FileResponse("templates/register.html")


@app.get("/dashboard")
async def dashboard():
    return FileResponse("templates/dashboard.html")


@app.get("/subscribe")
async def subscribe_page():
    return FileResponse("templates/subscribe.html")


@app.get("/admin")
async def admin_page():
    return FileResponse("templates/admin.html")


@app.get("/admin-login")
async def admin_login():
    return FileResponse("templates/admin_login.html")


@app.get("/upload-page")
async def upload_page():
    return FileResponse("templates/upload.html")

from fastapi.responses import FileResponse

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/AILOGO.ico")


# ==========================================
# Job Storage
# ==========================================

jobs = {}

# ==========================================
# Background Worker
# ==========================================

def process_song(job_id: str, file_path: str):

    try:

        print("\n===================================")
        print("Processing Job :", job_id)
        print("Song :", file_path)
        print("===================================\n")

        # Change Status
        jobs[job_id]["status"] = "processing"

        # Convert Song
        karaoke_file = convert_to_karaoke(file_path)

        # Save Job Result
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["karaoke"] = karaoke_file
        jobs[job_id]["song"] = os.path.splitext(
            os.path.basename(file_path)
        )[0]

        print("Job Completed :", job_id)

        # =====================================
        # Save History
        # =====================================

        try:

            db = SessionLocal()

            history = History(

                user_id=jobs[job_id]["user_id"],

                original_song=os.path.basename(file_path),

                karaoke_song=os.path.basename(karaoke_file)

            )

            db.add(history)

            db.commit()

            db.close()

            print("History Saved")

        except Exception as e:

            print("History Error :", e)

        # =====================================
        # Delete Uploaded File
        # =====================================

        try:

            os.remove(file_path)

        except Exception:

            pass

    except Exception as e:

        jobs[job_id]["status"] = "failed"

        jobs[job_id]["error"] = str(e)

        print("Job Failed :", e)

        # ==========================================
# Upload API
# ==========================================

# ==========================================
# Upload API
# ==========================================

@app.post("/upload")
async def upload(

    user_id: int = Form(...),

    file: UploadFile = File(...)

):
    print("UPLOAD API CALLED")

    try:

        # -----------------------------
        # Check User
        # -----------------------------

        db = SessionLocal()

        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if not user:

            db.close()

            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        # -----------------------------
        # Check Subscription
        # -----------------------------

        if user.role != "admin":

            if user.subscription_status.lower() != "active":

                db.close()

                raise HTTPException(
                    status_code=403,
                    detail="Please purchase a subscription."
                )

        db.close()

        # -----------------------------
        # Check MP3
        # -----------------------------

        if not file.filename.lower().endswith(".mp3"):

            raise HTTPException(
                status_code=400,
                detail="Only MP3 files are allowed."
            )

        # -----------------------------
        # Save File
        # -----------------------------

        filename = str(uuid.uuid4()) + "_" + file.filename

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(filepath, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # -----------------------------
        # Create Job
        # -----------------------------

        job_id = str(uuid.uuid4())

        jobs[job_id] = {

            "user_id": user_id,

            "status": "queued",

            "karaoke": None,

            "song": None,

            "error": None

        }

        # -----------------------------
        # Background Thread
        # -----------------------------

        thread = threading.Thread(

            target=process_song,

            args=(job_id, filepath),

            daemon=True

        )

        thread.start()

        print("New Job :", job_id)

        return {

            "success": True,

            "job_id": job_id,

            "message": "Upload Successful."

        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )

        # ===================================================
# Status API
# ===================================================

@app.get("/status/{job_id}")
async def status(job_id: str):

    if job_id not in jobs:

        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    job = jobs[job_id]

    return {

        "success": True,

        "status": job["status"],

        "song": job["song"],

        "error": job["error"]

    }


# ===================================================
# Download API
# ===================================================

@app.get("/download/{job_id}")
async def download(job_id: str):

    if job_id not in jobs:

        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    job = jobs[job_id]

    if job["status"] != "completed":

        raise HTTPException(
            status_code=400,
            detail="Song is still processing."
        )

    karaoke_file = job["karaoke"]

    if karaoke_file is None:

        raise HTTPException(
            status_code=404,
            detail="Karaoke file missing."
        )

    if not os.path.exists(karaoke_file):

        raise HTTPException(
            status_code=404,
            detail="Karaoke file not found."
        )

    return FileResponse(

        path=karaoke_file,

        filename=f"{job['song']}_karaoke.wav",

        media_type="audio/wav"

    )