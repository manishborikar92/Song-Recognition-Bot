# 🎵 Song Recognition Bot

Unleash the power of audio recognition with the **Song Recognition Bot**! Designed for Telegram, this bot lets you effortlessly identify songs from Instagram links, YouTube links, videos, audio files, or voice messages. By utilizing the ACRCloud API, the bot extracts audio, recognizes the track, and delivers detailed information like title, artist, album, release date, and streaming links for platforms such as YouTube and Spotify. Plus, the `/search` command allows users to download songs directly.

---

## 🚀 Key Features

- **Video Downloads Made Simple:** Easily download videos from shared links.
- **Accurate Song Identification:** Powered by the advanced ACRCloud API for precise results.
- **Detailed Song Information:** Receive metadata including title, artist, album, release date, and streaming links.
- **Song Search Functionality:** Quickly search and fetch song files with the `/search` command.

---

## 🛠️ Project Structure

```plaintext
Song-Recognition-Bot/
│  
├── data/
│   ├── audios/                # Temporary storage for audio files
│   ├── music/                 # Temporary storage for song files
│   └── videos/                # Temporary storage for video files
│
├── downloaders/
│   ├── instagram.py           # Functions for downloading Instagram videos and captions
│   ├── youtube.py             # Functions for downloading YouTube videos and captions
│   └── song.py                # Functions for downloading song files  
│
├── handlers/
│   ├── command.py             # Functions to handle commands
│   ├── message.py             # Functions to handle messages
│   └── check_membership.py    # Functions to manage Telegram channel membership
│
├── utils/
│   ├── audio_extractor.py     # Functions for audio extraction
│   ├── acrcloud_handler.py    # Functions for song recognition
│   └── cleardata.py           # Functions for cleaning temporary files
│
├── bot.py                     # Main entry point for the bot
├── config.py                  # Configuration settings
├── Dockerfile                 # Dockerfile for containerization
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── README.md                  # Documentation
```

---

## ⚙️ How to Set Up

### Prerequisites

- Python 3.7 or higher
- ACRCloud account and credentials
- Telegram Bot API token
- [FFmpeg](https://ffmpeg.org/) installed on your system

### Step 1: Clone the Repository

```bash
git clone https://github.com/manishborikar92/Song-Recognition-Bot.git
cd Song-Recognition-Bot
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the root directory and add the following:

```env
ACR_HOST=your_acr_host_url
ACR_ACCESS_KEY=your_acrcloud_access_key
ACR_ACCESS_SECRET=your_acrcloud_access_secret
ACR_ENDPOINT_URL=https://eu-api-v2.acrcloud.com/api/external-metadata/tracks
ACR_BEARER_TOKEN=your_acrcloud_bearer_token
BOT_TOKEN=your_telegram_bot_token
GROUP_ID=-1002267600531
CHANNEL_ID=-1002213319552
EXCEPTION_USER_ID=your_user_id
WEBHOOK_URL=<insert_render_or_railway_website_url_here>
```

### Step 4: Run the Bot

```bash
python bot.py
```

---

## 🐳 Deploying with Docker (Optional)

### Step 1: Build the Docker Image

```bash
docker build -t song-recognition-bot .
```

### Step 2: Run the Container

```bash
docker run -d --env-file .env --name song-recognition-bot song-recognition-bot
```

---

## 🌐 Deploying on Railway

1. Create a new project on [Railway](https://railway.app/).
2. Connect your GitHub repository.
3. Add environment variables in the "Settings" section using the `.env` file values.
4. Deploy the project.

---

## 🌐 Deploying on Render

1. Create a new service on [Render](https://render.com/).
2. Select your GitHub repository.
3. Add environment variables in the "Environment" section using the `.env` file values.
4. Deploy the project.

---

## 🧪 Testing

Ensure all components are functioning as expected by running:

```bash
python -m unittest discover
```

## 📖 How to Use

1. Start the bot on Telegram by sending `/start`.
2. Share a link (Instagram or YouTube), video, audio, or voice message with the bot.
3. Use `/search <song name, artist name>` to search for a specific song.
4. The bot will:
   - Download the video.
   - Extract audio.
   - Identify the song and share it along with its details.

---

## 🛡️ License

This project is licensed under the [GNU General Public License](LICENSE).

---

## 🙌 Acknowledgements

- [ProjectON3](https://t.me/ProjectON3) - Official Telegram channel for bots.
- [ACRCloud](https://www.acrcloud.com/) - Song recognition API.
- [FFmpeg](https://ffmpeg.org/) - Audio extraction tool.

---