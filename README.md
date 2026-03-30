# Text-Speech API (TTS + STT)

A **FastAPI** backend for natural speech synthesis and high-accuracy transcription, featuring safety filtering and secure user management.

---

## Features
- **🔊 TTS**: Natural speech generation via **Bark (Suno)**.
- **🗣️ STT**: Fast transcription via **faster-whisper**.
- **🛡️ Safety**: Integrated toxicity filtering (Detoxify).
- **🔐 Secure**: JWT-based OAuth2 authentication.
- **🗄️ Async DB**: SQLModel with MySQL for user/auth management.
- **🎨 UI Support**: Interactive frontend using **Streamlit** for better user experience.

---

## Project Structure


```text
.
├── audio/                 # Uploaded audio files (STT input)
├── outputs/               # Generated audio files (TTS output)
├── app.py                 # Streamlit UI application
├── main.py                # FastAPI entry point
├── pyproject.toml
├── README.md
├── .env.example           # Environment variables template (copy to .env and fill credentials)
└── src/
    ├── Database/          # Database models & configuration
    ├── repositories/      # Data access logic (auth, user)
    ├── routes/            # API endpoints (auth, user)
    ├── schema/            # Pydantic validation models
    ├── security/          # OAuth2 & security logic
    ├── services/          # Business logic (auth, user)
    ├── speech_to_text.py  # STT implementation
    ├── text_to_speech.py  # TTS implementation
    └── utils/             # Hashing & text verification
```
---

## Tech Stack
- **Framework**: FastAPI
- **Frontend/UI**: Streamlit
- **Models**: Bark (TTS), faster-whisper (STT), Detoxify (Safety)
- **Database**: MySQL (Async via SQLModel)
- **Auth**: JWT (OAuth2)

## API Endpoints

### Authentication
* **POST** `/register` — Create a new account
* **POST** `/login` — Get access token
* **GET** `/get-current-user` — Verify session

### Text to Speech
**POST** `/text-to-speech` (Requires Bearer Token)

**Request Body:**
```json
{
  "input_text": "Hello world",
  "lang_index": 0 
}
```

### Speech to Text
**POST** `/speech-to-text` (Requires Bearer Token)

**Body:** `file` (Form Data)

## Setup & Installation

### 1. Prerequisites
- **Python 3.12+**
- **uv**: [Install uv](https://github.com) (`curl -LsSf https://astral.sh | sh`)
- **FFmpeg**: Required for audio processing.
- **CUDA** (Optional): Recommended for GPU acceleration.

### 2. Installation
Clone the repository
```bash
git clone https://github.com/yash2k02/Text-Speech.git
cd Text-Speech
```
Install dependencies using uv
```
uv sync
```

### 3. Environment Configuration
Copy the .env.example file to .env and update it with your own credentials.

<!-- ### 4. Run the Application
```bash
uv run uvicorn main:app --reload
``` -->

### 4. Run Streamlit UI
```bash
streamlit run app.py
```

## Notes
 - TTS → STT is not lossless. The transcribed text may differ slightly from the original input.
Ensure FFmpeg is installed for audio conversion.
 - For GPU usage, install proper CUDA libraries; otherwise, CPU fallback works fine.


 > Currently, Streamlit directly calls backend functions (TTS/STT) instead of communicating via FastAPI endpoints. Integration via API (Streamlit ↔ FastAPI over HTTP) will be added later.  
 > The APIs can still be accessed and tested independently using tools like Postman or via the built-in Swagger UI.