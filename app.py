import os
import ffmpeg
from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
from pydub import AudioSegment, silence
from deepface import DeepFace
import cv2
import numpy as np
import speech_recognition as sr
from datetime import datetime
import yt_dlp
from waitress import serve

# --- Auto-detect base directory ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
CLIP_FOLDER = os.path.join(BASE_DIR, 'clips')

# --- Create folders if not exists ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLIP_FOLDER, exist_ok=True)

# --- Initialize Flask App ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Print debug info at startup ---
print(f"[INFO] Base directory: {BASE_DIR}")
print(f"[INFO] Uploads folder: {UPLOAD_FOLDER}")
print(f"[INFO] Clips folder  : {CLIP_FOLDER}")

# --- Helper Functions ---

def detect_loud_segments(audio_path, threshold=-20):
    try:
        audio = AudioSegment.from_file(audio_path)
        loud_segments = silence.detect_nonsilent(audio, min_silence_len=1000, silence_thresh=threshold)
        return [[start / 1000, end / 1000] for start, end in loud_segments]
    except Exception as e:
        print(f"[ERROR] Loud segment detection failed: {e}")
        return []

def extract_clip(input_path, start_time, duration, output_path):
    try:
        (
            ffmpeg
            .input(input_path, ss=start_time, t=duration)
            .output(output_path, vcodec='libx264', acodec='aac')
            .overwrite_output()
            .run(quiet=True)
        )
        print(f"[SUCCESS] Clip saved: {output_path}")
        return True
    except ffmpeg.Error as e:
        print(f"[ERROR] FFmpeg error: {e.stderr.decode()}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
    return False

def clip_video_process(video_path, video_name):
    date_folder = datetime.now().strftime('%Y-%m-%d')
    video_subfolder = os.path.join(UPLOAD_FOLDER, date_folder, video_name)
    os.makedirs(video_subfolder, exist_ok=True)

    audio_path = os.path.join(video_subfolder, f"{video_name}.wav")

    # Extract audio
    try:
        print(f"[INFO] Extracting audio from {video_path} → {audio_path}")
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, format='wav', ac=1, ar='16000')
            .overwrite_output()
            .run(quiet=True)
        )
    except Exception as e:
        print(f"[ERROR] Failed to extract audio: {e}")
        return []

    loud_segments = detect_loud_segments(audio_path)
    timestamps = [seg[0] for seg in loud_segments]

    clip_subfolder = os.path.join(CLIP_FOLDER, video_name)
    os.makedirs(clip_subfolder, exist_ok=True)
    clip_paths = []

    for idx, timestamp in enumerate(sorted(timestamps)):
        output_path = os.path.join(clip_subfolder, f"clip_{idx}.mp4")
        success = extract_clip(video_path, max(0, timestamp - 5), 15, output_path)
        if success:
            rel_path = os.path.relpath(output_path, CLIP_FOLDER).replace("\\", "/")
            clip_paths.append(url_for('serve_clip', filename=rel_path))

    return clip_paths

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({"error": "No video file part"}), 400
    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "No selected file"}), 400

    video_name = os.path.splitext(video.filename)[0]
    date_folder = datetime.now().strftime('%Y-%m-%d')
    video_subfolder = os.path.join(UPLOAD_FOLDER, date_folder, video_name)
    os.makedirs(video_subfolder, exist_ok=True)

    video_path = os.path.join(video_subfolder, video.filename)
    video.save(video_path)
    print(f"[INFO] Video saved to: {video_path}")

    clip_paths = clip_video_process(video_path, video_name)

    return jsonify({
        "clips": clip_paths
    })

@app.route('/download_link', methods=['POST'])
def download_link():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        'format': 'bv*[height<=1080]+ba/best[height<=1080]',
        'outtmpl': os.path.join(UPLOAD_FOLDER, 'input.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            video_name = info.get('title', 'livestream')
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

    clip_paths = clip_video_process(filename, video_name)

    return jsonify({
        "clips": clip_paths
    })

@app.route('/clips/<path:filename>')
def serve_clip(filename):
    return send_from_directory(CLIP_FOLDER, filename)

# --- Run App ---

if __name__ == "__main__":
    print("[INFO] Starting Flask app...")
    serve(app, host='0.0.0.0', port=5000)
