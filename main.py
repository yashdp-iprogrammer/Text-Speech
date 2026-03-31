from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from src.schema.schemas import TextToSpeech
# from src.utils.text_verification import verify_text
from src.security.o_auth import auth_dependency
from src.text_to_speech import text_to_speech
from fastapi import File, UploadFile
from src.speech_to_text import speech_to_text
from src.routes.auth import router as auth
from src.routes.user import router as user
from src.Database import db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db(db.engine)
    yield
    
app = FastAPI(title="Text-to-Speech", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


current_user = Annotated[dict, Depends(auth_dependency.get_current_user)]

app.include_router(auth)
app.include_router(user)

@app.get("/")
def health_check():
    return {"status": "TTS API is running"}


@app.post("/text-to-speech", tags=["Text-to-Speech"])
async def text_to_speech_api(user: current_user, request: TextToSpeech):
    try:
        email = user.get("email")

        # Validate input
        if not request.input_text:
            raise HTTPException(status_code=400, detail="Input text is required")

        # if not verify_text(request.input_text):
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Input contains unsafe/NSFW content"
        #     )

        # Generate speech
        result = text_to_speech(
            email=email,
            text=request.input_text,
            language=request.lang_index
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/speech-to-text", tags=["Speech-to-Text"])
async def speech_to_text_api(user:current_user, file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        result = speech_to_text(file)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))