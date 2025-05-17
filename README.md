# ClipsAI - Video Clipper

---

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
git clone https://github.com/yourusername/clipsai.git
cd clipsai

# Create and activate virtual environment
python3.9 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app in ClipsAI folder
open start_clipsai.bat
