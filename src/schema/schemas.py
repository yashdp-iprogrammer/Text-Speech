from pydantic import BaseModel, Field

# =========================
# Text-to-Speech Request
# =========================
class TextToSpeech(BaseModel):
    input_text: str = Field(..., min_length=1, description="Text to convert into speech")
    lang_index: int = Field(..., ge=0, description="Voice/language index")


# =========================
# Optional Response Schema
# =========================
class TTSResponse(BaseModel):
    status: str
    audio_url: str | None = None
    message: str | None = None
    
    

class SpeechToTextResponse(BaseModel):
    status: str
    text: str | None = None
    message: str | None = None