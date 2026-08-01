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
import traceback

from database import engine, SessionLocal
from models import Base, User, History

from auth import router as auth_router
from login import router as login_router
from user_profile import router as profile_router
from payment import router as payment_router
from admin import router as admin_router

from services.demucs_service import convert_to_karaoke
from sqlalchemy.orm import Session

# =====================================================
# DATABASE
# =====================================================

Base.metadata.create_all(bind=engine)


# =====================================================
# FASTAPI
# =====================================================

app = FastAPI(
    title="JoshAI Karaoke Generator",
    version="3.0"
)


# =====================================================
# ROUTERS
# =====================================================

app.include_router(auth_router)
app.include_router(login_router)
app.include_router(profile_router)
app.include_router(payment_router)
app.include_router(admin_router)


# =====================================================
# FOLDERS
# =====================================================

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "ai_output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)


# =====================================================
# STATIC FILES
# =====================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =====================================================
# HTML PAGES
# =====================================================

@app.get("/")
async def home():
    return FileResponse("templates/index.html")


@app.get("/index.html")
async def index():
    return FileResponse("templates/index.html")


@app.get("/login")
async def login():
    return FileResponse("templates/login.html")


@app.get("/register")
async def register():
    return FileResponse("templates/register.html")


@app.get("/dashboard")
async def dashboard():
    return FileResponse("templates/dashboard.html")


@app.get("/subscribe")
async def subscribe():
    return FileResponse("templates/subscribe.html")


@app.get("/admin")
async def admin():
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
# HEALTH CHECK
# =====================================================

@app.get("/health")
async def health():

    return {
        "status": "running",
        "version": "3.0"
    }


# =====================================================
# JOB STORAGE
# =====================================================

jobs = {}


# =====================================================
# FILE HELPERS
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
# BACKGROUND WORKER
# =====================================================

def process_song(job_id: str, filepath: str):

    print("\n==============================")
    print("THREAD STARTED")
    print("JOB :", job_id)
    print("FILE:", filepath)
    print("==============================")

    if job_id not in jobs:
        print("Job Missing")
        return

    try:

        jobs[job_id]["status"] = "processing"

        print("Calling Demucs...")

        karaoke_file = convert_to_karaoke(filepath)

        print("Demucs Finished")

        if not os.path.exists(karaoke_file):
            raise Exception("Output file not found.")

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["karaoke"] = karaoke_file
        jobs[job_id]["song"] = os.path.splitext(
            os.path.basename(filepath)
        )[0]

        print("Job Completed")

        try:

            db = SessionLocal()

            history = History(
                user_id=jobs[job_id]["user_id"],
                original_song=os.path.basename(filepath),
                karaoke_song=os.path.basename(karaoke_file)
            )

            db.add(history)
            db.commit()
            db.close()

            print("History Saved")

        except Exception as e:

            print("History Error")
            print(e)

        delete_file(filepath)

    except Exception as e:

        traceback.print_exc()

        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

        delete_file(filepath)

        print("JOB FAILED")
        print(e)
# =====================================================
# UPLOAD API
# =====================================================


@app.post("/upload")
async def upload(
    user_id: int = Form(...),
    file: UploadFile = File(...)
):
    print("\n==============================")
    print("UPLOAD REQUEST RECEIVED")
    print("==============================")

    db = SessionLocal()

    try:

        # -----------------------------
        # Check User
        # -----------------------------
        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        # -----------------------------
        # Check Subscription
        # -----------------------------
        if user.role.lower() != "admin":
            if user.subscription_status.lower() != "active":
                raise HTTPException(
                    status_code=403,
                    detail="Please purchase a subscription."
                )

        # -----------------------------
        # Validate File
        # -----------------------------
        if file.filename is None or file.filename.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="No file selected."
            )

        if not file.filename.lower().endswith(".mp3"):
            raise HTTPException(
                status_code=400,
                detail="Only MP3 files are allowed."
            )

        # -----------------------------
        # Create Upload Folder
        # -----------------------------
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # -----------------------------
        # Save Original Song Name
        # -----------------------------
        original_name = os.path.splitext(file.filename)[0]

        # -----------------------------
        # Safe Filename
        # -----------------------------
        unique_filename = (
            f"{original_name}_{uuid.uuid4().hex[:8]}.mp3"
        )

        filepath = os.path.join(
            UPLOAD_FOLDER,
            unique_filename
        )

        # -----------------------------
        # Save File
        # -----------------------------
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("File Saved :", filepath)

        # -----------------------------
        # Create Job
        # -----------------------------
        job_id = str(uuid.uuid4())

        jobs[job_id] = {
            "user_id": user.id,
            "status": "queued",
            "song": original_name,
            "karaoke": None,
            "error": None
        }

        print("Job Created :", job_id)

        # -----------------------------
        # Background Thread
        # -----------------------------
        thread = threading.Thread(
            target=process_song,
            args=(job_id, filepath),
            daemon=True
        )

        thread.start()

        print("Background Thread Started")

        return {
            "success": True,
            "job_id": job_id,
            "status": "queued",
            "song": original_name,
            "message": "Upload Successful"
        }

    except HTTPException:
        raise

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()

# =====================================================
# STATUS API
# =====================================================

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

        "job_id": job_id,

        "status": job["status"],

        "song": job["song"],

        "error": job["error"]

    }


# =====================================================
# DOWNLOAD API
# =====================================================

@app.get("/download/{job_id}")
async def download(job_id: str):

    if job_id not in jobs:

        raise HTTPException(
            status_code=404,
            detail="Job not found."
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
            detail="Output file missing."
        )

    if not os.path.exists(karaoke_file):

        raise HTTPException(
            status_code=404,
            detail="Karaoke file not found."
        )

    print("Download :", karaoke_file)

    return FileResponse(

        path=karaoke_file,

        filename=f"{job['song']}_karaoke.wav",

        media_type="audio/wav"

    )


# =====================================================
# END OF APP.PY
# =====================================================

print("===================================")
print("JoshAI Karaoke Generator Started")
print("===================================")