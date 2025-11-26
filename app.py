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
        err = e.stderr or e.stdout or str(e)
        raise RuntimeError(err.strip())
    
def save_upload(file_storage, folder: str) -> str:
    """Save uploaded file and return full path."""
    filename = unique_filename(file_storage.filename)
    path = os.path.join(folder, filename)
    file_storage.save(path)
    return path

# ------------------
# Routes 
# ------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/compress", methods=["GET", "POST"])
def compress():
    if request.method == "GET":
        return render_template("compress.html")
    file = request.files.get("video")
    if not file or file.filename == "":
        flash("No file selected.")
        return redirect(request.url)
    if not allowed_file(file.filename):
        flash("Unsupported file type.")
        return redirect(request.url)

    crf = request.form.get("crf", "28")
    try:
        crf_val = int(crf)
        if not (10 <= crf_val <= 51):
            raise ValueError()
    except ValueError:
        flash("CRF must be an integer between 10 and 51.")
        return redirect(request.url)

    in_path = save_upload(file)
    out_name = f"{uuid.uuid4().hex[:8]}_compressed.mp4"
    out_path = Path(app.config["PROCESSED_DIR"]) / out_name

    cmd = ["ffmpeg", "-y", "-i", in_path, "-vcodec", "libx264", "-crf", str(crf_val), "-preset", "medium", str(out_path)]
    try:
        run_ffmpeg(cmd)
    except RuntimeError as e:
        flash(f"Compression failed: {e}")
        return redirect(request.url)

    return redirect(url_for("download_file", filename=out_name))

@app.route("/convert", methods=["GET", "POST"])
def convert():
    if request.method == "GET":
        return render_template("convert.html")
    file = request.files.get("video")
    if not file or file.filename == "":
        flash("No file selected.")
        return redirect(request.url)
    if not allowed_file(file.filename):
        flash("Unsupported file type.")
        return redirect(request.url)

    audio_format = request.form.get("format", "mp3").lower()
    codec_map = {"mp3":"libmp3lame", "wav":"pcm_s16le", "aac":"aac", "m4a":"aac"}
    if audio_format not in codec_map:
        flash("Unsupported audio format.")
        return redirect(request.url)

    in_path = save_upload(file)
    out_name = f"{uuid.uuid4().hex[:8]}.{audio_format}"
    out_path = Path(app.config["PROCESSED_DIR"]) / out_name

    cmd = ["ffmpeg", "-y", "-i", in_path, "-vn", "-acodec", codec_map[audio_format], str(out_path)]
    try:
        run_ffmpeg(cmd)
    except RuntimeError as e:
        flash(f"Conversion failed: {e}")
        return redirect(request.url)

    return redirect(url_for("download_file", filename=out_name))

