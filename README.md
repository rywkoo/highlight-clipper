# Highlight Clipper

---

## 👀 Introduction

I'm just a starter or a student who just want to make this thing work, everything is made using AI, if something wrong I might not be able to help you.
If you are a senior, please help suggesting somewhere I can improve, thank you.

## 🚀 Features

- Upload local video files or provide YouTube/Twitch livestream links  
- Automatically download livestreams and save to uploads folder  
- Detect loud audio segments, laughter, emotions, and specific topics  
- Automatically generate video clips around detected moments  
- Preview clips in a clean and responsive web UI  

---

## 💻 Requirements

- Python 3.9  
- ffmpeg installed and in your PATH  
- Optional: NVIDIA GPU for faster video processing and emotion detection  

---

## ⚙️ Setup & Run

```bash
# Clone repo
git clone https://github.com/yourusername/highlight-clipper.git
cd highlight-clipper

# Create and activate virtual environment
py 3.9 -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app in ClipsAI folder
open start_clipsai.bat
