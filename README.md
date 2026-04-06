# Text-Speech API

A **FastAPI** backend for natural speech synthesis and high-accuracy transcription, with a **Streamlit** UI for local testing. Includes toxicity filtering and JWT-based authentication.

---

## Features

- **Text to Speech** — Natural, multilingual audio generation via [Suno Bark](https://github.com/suno-ai/bark) or [Groq API](https://console.groq.com/keys) *(quick testing)*
- **Speech to Text** — Fast, accurate transcription via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) or [Groq API](https://console.groq.com/keys) *(quick testing)*
  - ⚠️ **Pre-recorded audio files only** — This version supports uploading and transcribing pre-recorded audio files
  - 🎤 **Looking for real-time STT?** Check the [`realtime-stt`](https://github.com/yash2k02/Text-Speech/tree/realtime-stt) branch for live audio recording
- **Safety Filtering** — Toxicity detection on both input text and transcribed output via [Detoxify](https://github.com/unitaryai/detoxify)
- **Auth** — JWT-based OAuth2 authentication for protected endpoints
- **Async DB** — SQLModel + MySQL for user and auth management
- **Streamlit UI** — Interactive frontend for testing TTS and STT locally

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| UI | Streamlit |
| TTS Model | Suno Bark (`suno/bark`) or orpheus-v1-english(Groq API) |
| STT Model | faster-whisper or Whisper (Groq API) |
| Safety | Detoxify |
| Auth | JWT (python-jose) + OAuth2 |
| Database | MySQL (async via SQLModel + aiomysql) |
| Package Manager | [uv](https://docs.astral.sh/uv/) |

---

## Project Structure

```text
.
├── app.py                 # Streamlit UI
├── main.py                # FastAPI entry point
├── pyproject.toml
├── .env.example           # Environment variable template
├── audio/                 # Uploaded audio files (STT input)
├── outputs/               # Generated audio files (TTS output)
└── src/
    ├── Database/          # DB engine & session config
    ├── repositories/      # Data access layer (auth, user)
    ├── routes/            # API route definitions (auth, user)
    ├── schema/            # Pydantic request/response models
    ├── security/          # OAuth2 dependency & token logic
    ├── services/          # Business logic (auth, user)
    ├── speech_to_text.py  # STT implementation (faster-whisper)
    ├── text_to_speech.py  # TTS implementation (Bark)
    └── utils/
        ├── hash_util.py         # Password hashing (argon2)
        └── text_verification.py # Toxicity filtering (Detoxify)
```

---

## API Endpoints

### Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/register` | ❌ | Create a new user account |
| `POST` | `/login` | ❌ | Get a JWT access token |
| `GET` | `/get-current-user` | ✅ Bearer | Returns the current authenticated user |

**Login request body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Login response:**
```json
{
  "message": "Login successful",
  "access_token": access_token,
  "refresh_token": refresh_token,
  "token_type": "bearer"
}
```

---

### Text to Speech

| Method | Endpoint | Auth |
|--------|----------|------|
| `POST` | `/text-to-speech` | ✅ Bearer |

**Request body:**
```json
{
  "input_text": "Hello, how are you?",
  "lang_index": 0
}
```

**Response:**
```json
{
  "status": "success",
  "audio_url": "./outputs/<uuid>.mp3"
}
```

**Supported voices (`lang_index`):**

| Index | Voice Preset | Language |
|-------|-------------|----------|
| 0 | `v2/en_speaker_6` | English |
| 1 | `v2/en_speaker_9` | English |
| 2 | `v2/zh_speaker_0` | Chinese |
| 3 | `v2/zh_speaker_9` | Chinese |
| 4 | `v2/fr_speaker_0` | French |
| 5 | `v2/fr_speaker_1` | French |
| 6 | `v2/de_speaker_0` | German |
| 7 | `v2/de_speaker_3` | German |
| 8 | `v2/hi_speaker_2` | Hindi |
| 9 | `v2/hi_speaker_0` | Hindi |
| 10 | `v2/ja_speaker_2` | Japanese |
| 11 | `v2/ja_speaker_0` | Japanese |

---

### Speech to Text

| Method | Endpoint | Auth |
|--------|----------|------|
| `POST` | `/speech-to-text` | ✅ Bearer |

**Request:** multipart form with `file` field. Accepted formats: `.wav`, `.mp3`, `.m4a`, `.flac`

> **Note:** This version supports **pre-recorded audio files only**. The STT endpoint transcribes uploaded audio files and translates the output to English using `task="translate"`. All transcribed text is filtered for toxicity before being returned.

**Response:**
```json
{
  "status": "success",
  "text": "transcribed text here"
}
```

> ⚠️ **Real-time Speech-to-Text:** For live audio recording and real-time transcription capabilities, please check out the [`feature/realtime-stt`](https://github.com/yash2k02/Text-Speech/tree/feature/realtime-stt) branch.

---

## Setup & Installation

### Prerequisites

- **Python 3.10+**
- **uv** — [Install uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv.sh | sh`)
- **FFmpeg** — required for audio conversion
  - Linux: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **MySQL** — a running MySQL instance
- **CUDA** *(optional)* — GPU recommended for Bark TTS; CPU fallback works fine

### 1. Clone the repository

```bash
git clone https://github.com/yash2k02/Text-Speech.git
cd Text-Speech
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
# JWT Auth
LOGIN_SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
MY_SQL_USER=your_db_user
MY_SQL_PASSWORD=your_db_password
MY_SQL_HOST=localhost
MY_SQL_PORT=3306
MY_SQL_DB=your_db_name

# File Storage
BASE_OUTPUT_DIR=./outputs
BASE_AUDIO_DIR=./audio

# Groq API (for quick testing - get free key at https://console.groq.com/keys)
GROQ_API_KEY=your_groq_api_key_here

# Whisper Model (tiny / base / small / medium / large-v3)
WHISPER_MODEL_SIZE=large-v3

# Safety Filter (0.0–1.0; lower = stricter)
TOXICITY_THRESHOLD=0.3
```

### 4. Run the FastAPI backend

```bash
uv run uvicorn main:app --reload
```

API docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Run the Streamlit UI

```bash
uv run streamlit run app.py
```

> **Note:** The Streamlit app currently calls TTS/STT functions directly (bypassing HTTP). The FastAPI endpoints can still be tested independently via Swagger UI or Postman.

---

## Notes

- **Groq API for Quick Testing** — Both `text_to_speech.py` and `speech_to_text.py` include Groq API implementations for rapid prototyping. Simply switch the active implementation to use Groq's hosted models instead of local ones. Requires a free [Groq API key](https://console.groq.com/keys).
- **TTS output is not lossless for STT.** Transcribing Bark-generated audio may produce slightly different text than the original input — this is expected behaviour from the model.
- **Whisper translates to English.** The STT endpoint uses `task="translate"`, so all audio regardless of source language is transcribed in English.
- **Bark is slow on CPU.** The first TTS request also triggers model loading. A GPU with CUDA is strongly recommended for production use.
- **Detoxify runs on CPU** regardless of GPU availability, to keep memory usage predictable.