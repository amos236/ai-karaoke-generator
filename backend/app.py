from fastapi import FastAPI, UploadFile, File
import shutil
import os

app = FastAPI(
    title="AI Karaoke Generator",
    version="1.0.0"
)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def home():
    return {
        "message": "AI Karaoke Generator API is Running"
    }

@app.post("/upload")
async def upload_song(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Upload Successful",
        "filename": file.filename
    }