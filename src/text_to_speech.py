# import os
# import uuid
# import numpy as np
# import torch
# import scipy.io.wavfile as wavfile
# from transformers import AutoProcessor, BarkModel
# from pydub import AudioSegment
# from dotenv import load_dotenv
# # from src.utils.text_verification import verify_text
# from fastapi import HTTPException
# import time

# # Load env variables
# load_dotenv()


# BASE_OUTPUT_DIR = os.getenv("BASE_OUTPUT_DIR", "./outputs")

# processor = None
# model = None
# device = "cuda:0" if torch.cuda.is_available() else "cpu"

# def load_model():
#     global processor, model
#     if processor is None or model is None:
#         processor = AutoProcessor.from_pretrained("suno/bark")
#         model = BarkModel.from_pretrained("suno/bark").to(device)
#         model.eval()


# VOICE_OPTIONS = [
#     "v2/en_speaker_6", "v2/en_speaker_9",
#     "v2/zh_speaker_0", "v2/zh_speaker_9",
#     "v2/fr_speaker_0", "v2/fr_speaker_1",
#     "v2/de_speaker_0", "v2/de_speaker_3",
#     "v2/hi_speaker_2", "v2/hi_speaker_0",
#     "v2/ja_speaker_2", "v2/ja_speaker_0",
# ]


# def generate_audio_array(text: str, language: int):
#     load_model()

#     if language >= len(VOICE_OPTIONS):
#         raise ValueError("Invalid language index")

#     # audio_segments = []

#     # for segment in split_text(text):
#     #     try:
#     #         inputs = processor(
#     #             segment,
#     #             voice_preset=VOICE_OPTIONS[language],
#     #             return_tensors="pt"
#     #         ).to(device)

#     #         audio = model.generate(**inputs, min_eos_p=0.05)
#     #         audio_segments.append(audio.squeeze().cpu().numpy())

#     #     except Exception as e:
#     #         raise RuntimeError(f"Error generating audio: {str(e)}")
    
    
#     # try:
#     #     with torch.no_grad():  # ✅ huge optimization
#     #         for segment in split_text(text):
#     #             inputs = processor(
#     #                 segment,
#     #                 voice_preset=VOICE_OPTIONS[language],
#     #                 return_tensors="pt"
#     #             ).to(device)

#     #             audio = model.generate(**inputs,min_eos_p=0.05)
#     #             audio_segments.append(audio.squeeze().cpu().numpy())

#     # except Exception as e:
#     #     raise RuntimeError(f"Error generating audio: {str(e)}")

#     # if not audio_segments:
#     #     raise ValueError("No audio generated from input text")

#     # return np.concatenate(audio_segments)
    
#     inputs = processor(
#                     text,
#                     voice_preset=VOICE_OPTIONS[language],
#                     return_tensors="pt"
#                 ).to(device)

#     audio = model.generate(**inputs)
#     audio_array = audio.squeeze().cpu().numpy()

#     return audio_array

# def save_audio_file(email: str, audio_array: np.ndarray):
#     os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

#     unique_id = str(uuid.uuid4())
#     wav_path = os.path.join(BASE_OUTPUT_DIR, f"{unique_id}.wav")
#     mp3_path = os.path.join(BASE_OUTPUT_DIR, f"{unique_id}.mp3")

#     try:
#         sample_rate = model.generation_config.sample_rate

#         # Save WAV
#         wavfile.write(wav_path, rate=sample_rate, data=audio_array)

#         # Convert to MP3
#         sound = AudioSegment.from_wav(wav_path)
#         sound.export(mp3_path, format="mp3")

#         # Remove temp wav
#         os.remove(wav_path)

#         return mp3_path

#     except Exception as e:
#         raise RuntimeError(f"Error saving audio: {str(e)}")



# def text_to_speech(email: str, text: str, language: int):
#     # if not verify_text(text):
#     #     raise HTTPException(status_code=400, detail="Unsafe content")

#     try:
#         start_time = time.perf_counter()

#         audio_array = generate_audio_array(text, language)
#         file_path = save_audio_file(email, audio_array)

#         end_time = time.perf_counter()
#         time_taken = round(end_time - start_time, 2)

#         return {
#             "status": "success",
#             "audio_url": file_path,
#             "time_taken": time_taken
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# ===================================== GROQ VERSION ====================================================================


import os
import uuid
from groq import Groq
from dotenv import load_dotenv
from fastapi import HTTPException
import time

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
BASE_OUTPUT_DIR = os.getenv("BASE_OUTPUT_DIR", "./outputs")

VOICE_OPTIONS = ["autumn", "diana", "hannah", "austin", "daniel", "troy"]


def generate_audio_file(text: str, voice_index: int):
    if voice_index >= len(VOICE_OPTIONS):
        raise ValueError("Invalid voice index")

    try:
        response = client.audio.speech.create(
            model="canopylabs/orpheus-v1-english",
            voice=VOICE_OPTIONS[voice_index],
            input=text,
            response_format="wav"
        )

        audio_bytes = response.read() if hasattr(response, "read") else response
        return audio_bytes

    except Exception as e:
        raise RuntimeError(f"Groq API Error: {str(e)}")


def save_audio_file(audio_bytes: bytes):
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

    unique_id = str(uuid.uuid4())
    mp3_path = os.path.join(BASE_OUTPUT_DIR, f"{unique_id}.mp3")

    with open(mp3_path, "wb") as f:
        f.write(audio_bytes)

    return mp3_path


def text_to_speech(email: str, text: str, language: int):
    try:
        start_time = time.perf_counter()

        audio_bytes = generate_audio_file(text, language)
        file_path = save_audio_file(audio_bytes)

        time_taken = round(time.perf_counter() - start_time, 2)

        return {
            "status": "success",
            "audio_url": file_path,
            "time_taken": time_taken
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))