# Highlight Clipper

---

## 👀 Introduction

- I'm just a starter or a student who just want to make this thing work, everything is made using AI, if something wrong I might not be able to help you.
- This is just an early stage development, so everything won't be working like it would be like clipping via emotion and stuff will come with later update.
- If you are a senior, please help suggesting somewhere I can improve, thank you.

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
- ffmpeg installed and in your PATH  https://www.gyan.dev/ffmpeg/builds/
- High end CUDA 12.8
- Make sure to set the all of them in System Virables in Environment Variable

---

## ⚙️ Setup & Run

- Stay in the Path you wish to install in Window Explorer
- Click on the path above (Where you copy path) and write ```cmd```

```
git clone https://github.com/rywkoo/highlight-clipper.git
cd highlight-clipper
```

```
py -3.9 -m venv venv
venv\Scripts\activate
```

```
pip install -r requirements.txt
```

- Please run this separated installation
```
pip install torch==2.7.0+cu128 --index-url https://download.pytorch.org/whl/cu128
pip install torchvision==0.18.0+cu128 --index-url https://download.pytorch.org/whl/cu128
pip install torchaudio==2.7.0+cu128 --index-url https://download.pytorch.org/whl/cu128
```

- Open the ```start-h.bat``` inside the Directory and Enjoy
