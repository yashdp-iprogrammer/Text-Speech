import os
import uuid
import numpy as np
import regex
import torch
import scipy.io.wavfile as wavfile
from transformers import AutoProcessor, BarkModel
from pydub import AudioSegment
# import boto3
# from botocore.client import Config
from dotenv import load_dotenv
# from src.utils.text_verification import verify_text
from fastapi import HTTPException

# Load env variables
load_dotenv()


BASE_OUTPUT_DIR = os.getenv("BASE_OUTPUT_DIR", "./outputs")
# AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
# AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
# BUCKET_NAME = os.getenv("BUCKET_NAME")


processor = None
model = None
device = "cuda:0" if torch.cuda.is_available() else "cpu"

def load_model():
    global processor, model
    if processor is None or model is None:
        processor = AutoProcessor.from_pretrained("suno/bark")
        model = BarkModel.from_pretrained("suno/bark").to(device)


VOICE_OPTIONS = [
    "v2/en_speaker_6", "v2/en_speaker_9",
    "v2/zh_speaker_0", "v2/zh_speaker_9",
    "v2/fr_speaker_0", "v2/fr_speaker_1",
    "v2/de_speaker_0", "v2/de_speaker_3",
    "v2/hi_speaker_2", "v2/hi_speaker_0",
    "v2/ja_speaker_2", "v2/ja_speaker_0",
]


def split_text(text: str):
    """Split text into smaller segments for better audio generation."""
    segments = [seg.strip() for seg in regex.split(r"[,.]", text) if seg.strip()]
    return segments


def generate_audio_array(text: str, language: int):
    load_model()

    if language >= len(VOICE_OPTIONS):
        raise ValueError("Invalid language index")

    audio_segments = []

    for segment in split_text(text):
        try:
            inputs = processor(
                segment,
                voice_preset=VOICE_OPTIONS[language],
                return_tensors="pt"
            ).to(device)

            audio = model.generate(**inputs, min_eos_p=0.05)
            audio_segments.append(audio.squeeze().cpu().numpy())

        except Exception as e:
            raise RuntimeError(f"Error generating audio: {str(e)}")

    if not audio_segments:
        raise ValueError("No audio generated from input text")

    return np.concatenate(audio_segments)


def save_audio_file(email: str, audio_array: np.ndarray):
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

    unique_id = str(uuid.uuid4())
    wav_path = os.path.join(BASE_OUTPUT_DIR, f"{unique_id}.wav")
    mp3_path = os.path.join(BASE_OUTPUT_DIR, f"{unique_id}.mp3")

    try:
        sample_rate = model.generation_config.sample_rate

        # Save WAV
        wavfile.write(wav_path, rate=sample_rate, data=audio_array)

        # Convert to MP3
        sound = AudioSegment.from_wav(wav_path)
        sound.export(mp3_path, format="mp3")

        # Remove temp wav
        os.remove(wav_path)

        return mp3_path

    except Exception as e:
        raise RuntimeError(f"Error saving audio: {str(e)}")


# s3_client = boto3.client(
#     "s3",
#     config=Config(signature_version="s3v4"),
#     region_name=AWS_REGION,
#     aws_access_key_id=AWS_ACCESS_KEY,
#     aws_secret_access_key=AWS_SECRET_KEY,
# )

# def upload_to_s3(file_path: str, email: str):
#     if not BUCKET_NAME:
#         raise ValueError("BUCKET_NAME not set in environment")

#     file_name = os.path.basename(file_path)
#     s3_key = f"tts/{email}/{file_name}"

#     try:
#         s3_client.upload_file(file_path, BUCKET_NAME, s3_key)

#         url = s3_client.generate_presigned_url(
#             "get_object",
#             Params={"Bucket": BUCKET_NAME, "Key": s3_key},
#             ExpiresIn=3600
#         )

#         return url

#     except Exception as e:
#         raise RuntimeError(f"S3 upload failed: {str(e)}")


# def text_to_speech(email: str, text: str, language: int):
#     """
#     Main function to generate speech and upload to S3.
#     Returns: public URL
#     """
#     if not verify_text(text):
#             raise HTTPException(
#                 status_code=400,
#                 detail="Input contains unsafe/NSFW content"
#             )

#     try:
#         audio_array = generate_audio_array(text, language)
#         print(audio_array[:10])
#         print(audio_array.max(), audio_array.min())
#         file_path = save_audio_file(email, audio_array)
#         # url = upload_to_s3(file_path, email)

#         return {
#             "status": "success",
#             "audio_url": file_path
#         }

#     except Exception as e:
#         return {
#             "status": "error",
#             "message": str(e)
#         }


def text_to_speech(email: str, text: str, language: int):
    # if not verify_text(text):
    #     raise HTTPException(status_code=400, detail="Unsafe content")

    try:
        audio_array = generate_audio_array(text, language)
        file_path = save_audio_file(email, audio_array)

        return {
            "status": "success",
            "audio_url": file_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))