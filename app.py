import os
import ffmpeg
import numpy as np
from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
from pydub import AudioSegment, silence
from deepface import DeepFace
import cv2
import speech_recognition as sr
from datetime import datetime
import yt_dlp
from waitress import serve

# GPU Configuration
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Use first GPU

# PyTorch GPU check
def check_gpu():
    try:
        import torch
        if torch.cuda.is_available():
            print(f"GPU is available: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("GPU not available. Running on CPU.")
            return False
    except Exception as e:
        print("Error initializing GPU with PyTorch:", e)
        return False

gpu_available = check_gpu()

app = Flask(__name__)

# --- Use absolute paths based on script location ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
CLIP_FOLDER = os.path.join(BASE_DIR, 'clips')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLIP_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
print(f"[DEBUG] UPLOAD_FOLDER: {UPLOAD_FOLDER}")
print(f"[DEBUG] CLIP_FOLDER: {CLIP_FOLDER}")

# Helper Functions

def detect_loud_segments(audio_path, threshold=-20):
    try:
        audio = AudioSegment.from_file(audio_path)
        loud_segments = silence.detect_nonsilent(audio, min_silence_len=1000, silence_thresh=threshold)
        print(f"[DEBUG] Loud segments detected in {audio_path}: {loud_segments}")
        return loud_segments
    except Exception as e:
        print(f"[ERROR] Failed to detect loud segments: {e}")
        return []

def extract_clip(input_path, start_time, duration, output_path):
    try:
        print(f"[DEBUG] Extracting clip: {input_path} -> {output_path}, start={start_time}, duration={duration}")
        (
            ffmpeg
            .input(input_path, ss=start_time, t=duration)
            .output(output_path, vcodec='h264_nvenc', acodec='copy')
            .overwrite_output()
            .run(quiet=True)
        )
        print(f"[SUCCESS] Clip saved: {output_path}")
        return True
    except ffmpeg.Error as e:
        print(f"[ERROR] FFmpeg error extracting clip: {e.stderr.decode()}")
    except Exception as e:
        print(f"[ERROR] General error extracting clip: {e}")
    return False

def clip_video_process(video_path, video_name):
    date_folder = datetime.now().strftime('%Y-%m-%d')
    video_subfolder = os.path.join(UPLOAD_FOLDER, date_folder, video_name)
    os.makedirs(video_subfolder, exist_ok=True)

    audio_path = os.path.join(video_subfolder, f"{video_name}.wav")

    # Extract audio
    try:
        print(f"[DEBUG] Extracting audio from {video_path} to {audio_path}")
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, format='wav', ac=1, ar='16000')
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as e:
        print(f"[ERROR] FFmpeg error extracting audio: {e.stderr.decode()}")
        return [], []
    except Exception as e:
        print(f"[ERROR] General error extracting audio: {e}")
        return [], []

    loud_segments = detect_loud_segments(audio_path)
    print(f"[DEBUG] Loud segments: {loud_segments}")

    timestamps = [seg[0] / 1000.0 for seg in loud_segments]

    clip_subfolder = os.path.join(CLIP_FOLDER, video_name)
    os.makedirs(clip_subfolder, exist_ok=True)
    clip_paths = []
    current_time = 0

    for idx, timestamp in enumerate(sorted(timestamps)):
        if timestamp >= current_time:
            output_path = os.path.join(clip_subfolder, f"clip_{idx}.mp4")
            start_time = max(0, timestamp - 10)  # 10 sec before
            duration = 20  # 20 sec long
            success = extract_clip(video_path, start_time, duration, output_path)
            if success:
                rel_path = os.path.relpath(output_path, CLIP_FOLDER).replace("\\", "/")
                clip_paths.append(url_for('serve_clip', filename=rel_path))
            current_time = timestamp + 20  # skip ahead

    return clip_paths, []

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
    print(f"[DEBUG] Video saved to: {video_path}")

    clip_paths, topic_segments = clip_video_process(video_path, video_name)

    return jsonify({
        "clips": clip_paths,
        "topics": topic_segments
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

    clip_paths, topic_segments = clip_video_process(filename, video_name)

    return jsonify({
        "clips": clip_paths,
        "topics": topic_segments
    })

@app.route('/clips/<path:filename>')
def serve_clip(filename):
    print(f"[DEBUG] Serving clip: {filename}")
    return send_from_directory(CLIP_FOLDER, filename)

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
