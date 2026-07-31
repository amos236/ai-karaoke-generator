from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Form
)

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import os
import shutil
import uuid
import threading
import glob

from database import engine, SessionLocal
from models import Base, User, History

from auth import router as auth_router
from login import router as login_router
from profile import router as profile_router
from payment import router as payment_router
from admin import router as admin_router

from services.demucs_service import convert_to_karaoke


# =====================================================
# Create Database Tables
# =====================================================

Base.metadata.create_all(bind=engine)


# =====================================================
# FastAPI App
# =====================================================

app = FastAPI(
    title="JoshAI Karaoke Generator",
    version="3.0"
)


# =====================================================
# Include Routers
# =====================================================

app.include_router(auth_router)
app.include_router(login_router)
app.include_router(profile_router)
app.include_router(payment_router)
app.include_router(admin_router)


# =====================================================
# Folder Configuration
# =====================================================

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "ai_output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)


# =====================================================
# Static Files
# =====================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =====================================================
# HTML Pages
# =====================================================

@app.get("/")
async def home():
    return FileResponse("templates/index.html")


@app.get("/index.html")
async def index_page():
    return FileResponse("templates/index.html")


@app.get("/login")
async def login_page():
    return FileResponse("templates/login.html")


@app.get("/register")
async def register_page():
    return FileResponse("templates/register.html")


@app.get("/dashboard")
async def dashboard_page():
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


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/AILOGO.ico")


# =====================================================
# Health Check
# =====================================================

@app.get("/health")
async def health():
    return {
        "status": "running",
        "message": "JoshAI Karaoke Generator API"
    }


# =====================================================
# Temporary Job Storage
# =====================================================

jobs = {}


# =====================================================
# Utility
# =====================================================

def delete_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def delete_folder(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception:
        pass

# =====================================================
# Background Worker
# =====================================================

def process_song(job_id: str, file_path: str):

    try:

        print("\n========================================")
        print("Starting Job :", job_id)
        print("Input File   :", file_path)
        print("========================================")

        if job_id not in jobs:
            return

        jobs[job_id]["status"] = "processing"

        # -------------------------------------
        # Run Demucs
        # -------------------------------------

        karaoke_file = convert_to_karaoke(file_path)

        # -------------------------------------
        # Verify Output
        # -------------------------------------

        if not os.path.exists(karaoke_file):

            raise Exception(
                "Karaoke file was not generated."
            )

        jobs[job_id]["status"] = "completed"

        jobs[job_id]["karaoke"] = karaoke_file

        jobs[job_id]["song"] = os.path.splitext(
            os.path.basename(file_path)
        )[0]

        print("\n========================================")
        print("Job Completed")
        print("Output :", karaoke_file)
        print("========================================")

        # -------------------------------------
        # Save History
        # -------------------------------------

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

            print("History Saved Successfully")

        except Exception as history_error:

            print("History Error :", history_error)

        # -------------------------------------
        # Delete Uploaded MP3
        # -------------------------------------

        delete_file(file_path)

    except Exception as e:

        print("\n========================================")
        print("JOB FAILED")
        print(e)
        print("========================================")

        if job_id in jobs:

            jobs[job_id]["status"] = "failed"

            jobs[job_id]["error"] = str(e)

        delete_file(file_path)

# =====================================================
# Upload API
# =====================================================

@app.post("/upload")
async def upload(
    user_id: int = Form(...),
    file: UploadFile = File(...)
):

    print("\n========== UPLOAD REQUEST ==========")

    db = SessionLocal()

    try:

        # -------------------------------------
        # User Check
        # -------------------------------------

        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if user is None:

            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        # -------------------------------------
        # Subscription Check
        # -------------------------------------

        if user.role.lower() != "admin":

            if user.subscription_status.lower() != "active":

                raise HTTPException(
                    status_code=403,
                    detail="Subscription required."
                )

        # -------------------------------------
        # File Validation
        # -------------------------------------

        if file.filename is None:

            raise HTTPException(
                status_code=400,
                detail="No file selected."
            )

        if not file.filename.lower().endswith(".mp3"):

            raise HTTPException(
                status_code=400,
                detail="Only MP3 files are allowed."
            )

        # -------------------------------------
        # Save Uploaded File
        # -------------------------------------

        unique_name = str(uuid.uuid4())

        filename = unique_name + ".mp3"

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(filepath, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # -------------------------------------
        # Create Job BEFORE Starting Thread
        # -------------------------------------

        job_id = str(uuid.uuid4())

        jobs[job_id] = {

            "user_id": user.id,

            "status": "queued",

            "karaoke": None,

            "song": None,

            "error": None

        }

        # -------------------------------------
        # Start Background Thread
        # -------------------------------------

        thread = threading.Thread(

            target=process_song,

            args=(job_id, filepath),

            daemon=True

        )

        thread.start()

        print("Job Created :", job_id)

        return {

            "success": True,

            "job_id": job_id,

            "status": "queued"

        }

    finally:

        db.close()


# =====================================================
# Status API
# =====================================================

@app.get("/status/{job_id}")
async def get_status(job_id: str):

    if job_id not in jobs:

        raise HTTPException(

            status_code=404,

            detail="Invalid Job ID."

        )

    job = jobs[job_id]

    return {

        "success": True,

        "job_id": job_id,

        "status": job["status"],

        "song": job["song"],

        "error": job["error"]

    }


# =====================================================
# Download API
# =====================================================

@app.get("/download/{job_id}")
async def download(job_id: str):

    if job_id not in jobs:

        raise HTTPException(

            status_code=404,

            detail="Invalid Job ID."

        )

    job = jobs[job_id]

    if job["status"] == "failed":

        raise HTTPException(

            status_code=400,

            detail=job["error"]

        )

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

            detail="Output file not found."

        )

    return FileResponse(

        path=karaoke_file,

        filename=f"{job['song']}_karaoke.wav",

        media_type="audio/wav"

    )