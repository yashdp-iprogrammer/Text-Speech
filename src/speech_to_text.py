# import os
# import uuid
# import time
# import torch
# from src.utils.text_verification import verify_text
# from faster_whisper import WhisperModel 
# from fastapi import HTTPException


# MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
# BASE_AUDIO_DIR = os.getenv("BASE_AUDIO_DIR", "./audio")
# ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac"}



# _model = None

# def get_model():
#     global _model
#     if _model is None:
#         device = "cuda" if torch.cuda.is_available() else "cpu"
#         print("Loading whisper model on device:", device)
#         _model = WhisperModel(MODEL_SIZE, device="cpu")
#     return _model

# # =========================
# # Save Uploaded File
# # =========================
# def save_audio_file(file):
#     os.makedirs(BASE_AUDIO_DIR, exist_ok=True)

#     file_id = str(uuid.uuid4())
#     file_path = os.path.join(BASE_AUDIO_DIR, f"{file_id}_{file.filename}")

#     with open(file_path, "wb") as f:
#         f.write(file.file.read())

#     return file_path

# # =========================
# # Speech to Text
# # =========================
# def speech_to_text(file):
#     try:
#         start_time = time.perf_counter()

#         model = get_model()
#         file_path = save_audio_file(file)
        
#         ext = os.path.splitext(file.filename)[1].lower()
#         if ext not in ALLOWED_EXTENSIONS:
#             raise HTTPException(status_code=400, detail="Unsupported file format")

#         segments, _ = model.transcribe(file_path, task="translate",temperature=0)

#         text = " ".join(segment.text for segment in segments)

#         if not verify_text(text):
#             raise HTTPException(status_code=400, detail="Unsafe content")

#         end_time = time.perf_counter()

#         return {
#             "status": "success",
#             "text": text.strip(),
#             "time_taken": round(end_time - start_time, 2)
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# ===================================== GROQ VERSION ====================================================================

import os
import uuid
import time
from fastapi import HTTPException
from groq import AsyncGroq
from src.utils.text_verification import verify_text

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac"}
BASE_AUDIO_DIR = os.getenv("BASE_AUDIO_DIR", "./audio")

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))


# =========================
# Save Uploaded File
# =========================
def save_audio_file(file, file_bytes):
    os.makedirs(BASE_AUDIO_DIR, exist_ok=True)

    file_id = str(uuid.uuid4())
    file_path = os.path.join(BASE_AUDIO_DIR, f"{file_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return file_path


# =========================
# Speech to English
# =========================
async def speech_to_text(file):
    try:
        start_time = time.perf_counter()

        # Check file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Read uploaded file
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty file")

        # Save file locally
        file_path = save_audio_file(file, audio_bytes)

        # Call Groq API for transcription
        response = await client.audio.translations.create(
            file=(file.filename, audio_bytes),
            model="whisper-large-v3",
            temperature=0
        )

        text = response.text.strip()

        # Verify text safety
        if not verify_text(text):
            raise HTTPException(status_code=400, detail="Unsafe content")

        end_time = time.perf_counter()
        time_taken = round(end_time - start_time, 2)

        return {
            "status": "success",
            "text": text,
            "time_taken": time_taken,
            "saved_file_path": file_path  # ✅ return path to saved audio
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))