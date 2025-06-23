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
- Cuda 11.8: https://developer.nvidia.com/cuda-11-8-0-download-archive
- CuDNN 8.6: https://developer.nvidia.com/compute/cudnn/secure/8.6.0/local_installers/11.8/cudnn-windows-x86_64-8.6.0.163_cuda11-archive.zip
- Make sure to set the all of them in System Virables in Environment Variable

---

## ⚙️ Setup & Run

- Stay in the Path you wish to install in Window Explorer
- Click on the path above (Where you copy path) and write ```cmd```

```bash
git clone https://github.com/rywkoo/highlight-clipper.git
cd highlight-clipper
```

- Check your ```nvidia-smi``` in Command Prompt and look for your Cuda Version
- Open ```requirements.txt``` inside the Clone Repo and scroll down and change Cuda Version based on your current version of Cuda by add a "#" in front of the version you do not wish to install and leave blank in front of the version that match your version

```
py -3.9 -m venv venv
venv\Scripts\activate
```

```
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu128
```
- Open the ```start-h.bat``` inside the Directory and Enjoy
