import os
import uuid
import subprocess 
from flask import (
    Flask, render_template, request, redirect, url_for,
    send_from_directory, flash, current_app
)
from werkzeug.utils import secure_filename

# --------------
# Configuration
# --------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed") 
ALLOWED_EXT = {"mp4", "mov", "mkv", "avi", "webm", "flv"}

# ensure folder exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exists_ok=True)

# ----------------
# Flask App
# ----------------
app = Flask(__name__)
app.config["UPLOAD_DIR"] = UPLOAD_DIR
app.config["PROCESSED_DIR"] = PROCESSED_DIR
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# -------------
# Helpers
# -------------
def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1).lower() in ALLOWED_EXT

def unique_filename(filename: str) -> str:
    name = secure_filename(filename)
    uid = uuid.uuid().hex[:8]
    return f"{uid}_{name}"

def run_ffmpeg(cmd: list):
    """Execute ffmpeg command and raise RuntimeError on failure."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return proc.stdout
    except subprocess.CalledProcessorError as e:
        # include stderr to help debugging
        err = e.stderr or e.stdout or str(e)
        raise RuntimeError(err.strip())
    
def save_upload(file_storage, folder: str) -> str:
    """Save uploaded file and return full path."""
    filename = unique_filename(file_storage.filename)
    path = os.path.join(folder, filename)
    file_storage.save(path)
    return path

# ------------------
# Routes - Dashboard
# ------------------
@app.route("/")
def index():
    return render_template("index.html")
