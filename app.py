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

# Directory Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define upload and clip folders relative to BASE_DIR (your Git repo root)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
CLIP_FOLDER = os.path.join(BASE_DIR, 'clips')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLIP_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper Functions

def detect_loud_segments(audio_path, threshold=-20):
    audio = AudioSegment.from_file(audio_path)
    loud_segments = silence.detect_nonsilent(audio, min_silence_len=1000, silence_thresh=threshold)
    return loud_segments  # list of [start_ms, end_ms]

def detect_laughter(audio_path):
    import librosa
    y, sr_ = librosa.load(audio_path, sr=None)
    rms = librosa.feature.rms(y=y)[0]
    threshold = np.percentile(rms, 90)
    laughter_frames = np.where(rms > threshold)[0]
    times = librosa.frames_to_time(laughter_frames, sr=sr_)
    return times

def detect_emotions(video_path):
    cap = cv2.VideoCapture(video_path)
    emotion_frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False,
                                     detector_backend='opencv',
                                     device='cuda' if gpu_available else 'cpu')
            dominant_emotion = result.get('dominant_emotion', '')
            if dominant_emotion in ['happy', 'sad', 'angry']:
                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                emotion_frames.append(timestamp)
        except Exception:
            pass
    cap.release()
    return emotion_frames

def detect_topic(audio_path, keywords):
    recognizer = sr.Recognizer()
    topic_segments = []
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio).lower()
            for keyword in keywords:
                if keyword.lower() in text:
                    topic_segments.append((keyword, text))
        except sr.UnknownValueError:
            print("Speech not recognized")
        except Exception as e:
            print("Speech recognition error:", e)
    return topic_segments

def extract_clip(input_path, start_time, duration, output_path):
    try:
        (
            ffmpeg
            .input(input_path, ss=start_time, t=duration)
            .output(output_path, vcodec='h264_nvenc', acodec='copy')
            .overwrite_output()
            .run(quiet=True)
        )
        print(f"Clip saved: {output_path}")
    except ffmpeg.Error as e:
        print(f"Error extracting clip: {e.stderr.decode()}")
    except Exception as e:
        print(f"General error extracting clip: {e}")

def extract_around_timestamp(input_path, timestamp, output_path, skip_time=20):
    pre_duration = 30  # seconds before
    post_duration = 30  # seconds after
    start_time = max(0, timestamp - pre_duration)
    duration = pre_duration + post_duration
    extract_clip(input_path, start_time, duration, output_path)
    return timestamp + skip_time

def clip_video_process(video_path, video_name):
    video_subfolder = os.path.join(UPLOAD_FOLDER, datetime.now().strftime('%Y-%m-%d'), video_name)
    os.makedirs(video_subfolder, exist_ok=True)

    audio_path = os.path.join(video_subfolder, f"{video_name}.wav")

    # Extract audio
    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, format='wav', ac=1, ar='16000')
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as e:
        print(f"Error extracting audio: {e.stderr.decode()}")
        return [], []
    except Exception as e:
        print(f"General error extracting audio: {e}")
        return [], []

    loud_segments = detect_loud_segments(audio_path)
    laughter_segments = detect_laughter(audio_path)
    emotion_timestamps = detect_emotions(video_path)
    topic_segments = detect_topic(audio_path, ['project', 'meeting', 'success'])

    loud_timestamps = [seg[0] / 1000.0 for seg in loud_segments]
    laughter_timestamps = list(laughter_segments)

    timestamps = set(loud_timestamps)
    timestamps.update(laughter_timestamps)
    timestamps.update(emotion_timestamps)

    clip_subfolder = os.path.join(CLIP_FOLDER, video_name)
    os.makedirs(clip_subfolder, exist_ok=True)
    clip_paths = []
    current_time = 0

    for idx, timestamp in enumerate(sorted(timestamps)):
        if timestamp >= current_time:
            output_path = os.path.join(clip_subfolder, f"clip_{idx}.mp4")
            current_time = extract_around_timestamp(video_path, timestamp, output_path)
            rel_path = os.path.relpath(output_path, CLIP_FOLDER).replace("\\", "/")
            clip_paths.append(url_for('serve_clip', filename=rel_path))

    return clip_paths, topic_segments

# Routes

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

    current_date = datetime.now().strftime('%Y-%m-%d')
    video_folder = os.path.join(UPLOAD_FOLDER, current_date)
    os.makedirs(video_folder, exist_ok=True)

    video_name = os.path.splitext(video.filename)[0]
    video_subfolder = os.path.join(video_folder, video_name)
    os.makedirs(video_subfolder, exist_ok=True)

    video_path = os.path.join(video_subfolder, video.filename)
    video.save(video_path)

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
    return send_from_directory(CLIP_FOLDER, filename)

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
