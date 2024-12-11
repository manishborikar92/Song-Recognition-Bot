# 🎵 Song Recognition Bot

A Telegram bot that helps you identify songs from Instagram reels by analyzing audio content using the ACRCloud API. The bot downloads the reel, extracts audio, and provides song details such as title, artist, album, release date, and YouTube link.

---

## 🚀 Features

- Download Instagram reels from links shared by users.
- Extract audio from the reels.
- Identify songs using the ACRCloud API.
- Share song details with users, including title, artist, album, and release date.

---

## 🛠️ Project Structure

```plaintext
telegram_instagram_music_bot/
│
├── bot.py                   # Main entry point for the bot
├── config.py                # Configuration settings (API keys, tokens, etc.)
├── requirements.txt         # List of Python dependencies
├── utils/
│   ├── instagram.py         # Functions to fetch Instagram video and caption
│   ├── audio_processing.py  # Functions to download and process audio
│   ├── acrcloud.py          # Functions to interact with ACRCloud API
│   ├── helpers.py           # Reusable utility functions
│
├── data/
│   ├── downloads/           # Folder for temporarily storing video and audio files
│   └── __init__.py          # Makes 'data' a Python package
│
└── README.md                # Documentation about the project
```

---

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.7 or higher
- ACRCloud account and credentials
- Telegram Bot API token
- [FFmpeg](https://ffmpeg.org/) installed on your system

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/music-finder-bot.git
cd music-finder-bot
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Credentials

- **ACRCloud**: Add your credentials in `bot.py`:
  ```python
  HOST = "https://identify-ap-southeast-1.acrcloud.com"
  ACCESS_KEY = "your_acrcloud_access_key"
  ACCESS_SECRET = "your_acrcloud_access_secret"
  ```
- **Telegram Bot Token**: Replace `"your_bot_token"` in `bot.py` with your bot token.

### 4️⃣ Run the Bot

```bash
python bot.py
```

---

## 🧪 Testing

Run the unit tests to ensure the components work as expected:

```bash
python -m unittest discover
```

---

## 🔧 Key Functions

### 1. `download_reel.py`
Downloads Instagram reels from a provided URL.

### 2. `extract_audio.py`
Extracts audio from a video file using FFmpeg.

### 3. `song_recognition.py`
Recognizes songs using the ACRCloud API.

---

## 📖 Usage Instructions

1. Start the bot on Telegram by sending `/start`.
2. Share an Instagram reel link with the bot.
3. The bot will:
   - Download the reel.
   - Extract audio from the video.
   - Identify the song and share the details with you.

---

## 🛡️ License

This project is licensed under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

- [Instaloader](https://instaloader.github.io/) for Instagram reel downloads.
- [ACRCloud](https://www.acrcloud.com/) for song recognition.
- [FFmpeg](https://ffmpeg.org/) for audio extraction.

---