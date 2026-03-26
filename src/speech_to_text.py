import os
import uuid
import torch
from src.utils.text_verification import verify_text
from faster_whisper import WhisperModel
from fastapi import HTTPException


MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
BASE_AUDIO_DIR = os.getenv("BASE_AUDIO_DIR", "./audio")
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac"}



_model = None

def get_model():
    global _model
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Loading whisper model on device:", device)
        _model = WhisperModel(MODEL_SIZE, device="cpu")
    return _model

# =========================
# Save Uploaded File
# =========================
def save_audio_file(file):
    os.makedirs(BASE_AUDIO_DIR, exist_ok=True)

    file_id = str(uuid.uuid4())
    file_path = os.path.join(BASE_AUDIO_DIR, f"{file_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path

# =========================
# Speech to Text
# =========================
# def speech_to_text(file):
#     try:
#         model = get_model()
#         file_path = save_audio_file(file)

#         segments, _ = model.transcribe(file_path)

#         text = ""
#         for segment in segments:
#             text += segment.text + " "


#         if not verify_text(text):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Input contains unsafe/NSFW content"
#             )
            
#         return {
#             "status": "success",
#             "text": text.strip()
#         }

#     except Exception as e:
#         return {
#             "status": "error",
#             "message": str(e)
#         }


def speech_to_text(file):
    try:
        model = get_model()
        file_path = save_audio_file(file)
        
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        segments, _ = model.transcribe(file_path)

        text = " ".join(segment.text for segment in segments)

        if not verify_text(text):
            raise HTTPException(status_code=400, detail="Unsafe content")

        return {
            "status": "success",
            "text": text.strip()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))