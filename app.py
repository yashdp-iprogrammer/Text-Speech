import streamlit as st
from src.text_to_speech import text_to_speech, VOICE_OPTIONS
from src.speech_to_text import speech_to_text

# --- Wrapper for Speech-to-Text compatibility ---
class StreamlitFileWrapper:
    """Wraps Streamlit UploadedFile to match the backend's expected object structure"""
    def __init__(self, uploaded_file):
        self.file = uploaded_file
        self.filename = uploaded_file.name

# --- Page Configuration ---
st.set_page_config(page_title="Text-Speech")

st.title("AI Text-Speech")
st.sidebar.title("Settings")
mode = st.sidebar.selectbox("Choose Mode", ["Text to Speech", "Speech to Text"])

# --- Mode 1: Text to Speech ---
if mode == "Text to Speech":
    st.header("Text to Speech")
    st.info("Using Suno Bark model for high-quality generation.")

    # Language/Voice Selection
    # VOICE_OPTIONS are imported from your backend file
    voice_index = st.selectbox(
        "Select Voice/Language", 
        range(len(VOICE_OPTIONS)), 
        format_func=lambda x: VOICE_OPTIONS[x]
    )

    user_text = st.text_area("Enter text to convert:", height=150, placeholder="Hello, how are you today?")
    
    if st.button("Generate Audio"):
        if not user_text.strip():
            st.error("Please enter some text.")
        else:
            with st.spinner("Generating audio (this may take a moment)..."):
                try:
                    result = text_to_speech("user@example.com", user_text, voice_index)

                    if result["status"] == "success":
                        st.success("Generation complete!")
                        st.audio(result["audio_url"])

                        with open(result["audio_url"], "rb") as f:
                            st.download_button("Download MP3", f, file_name="generated_audio.mp3")

                    else:
                        if "Unsafe content" in result["message"]:
                            st.warning("⚠️ Your input contains unsafe or toxic content. Please modify your text.")
                        else:
                            st.error(f"❌ Error: {result['message']}")

                except Exception as e:
                    error_msg = str(e)

                    if "Unsafe content" in error_msg:
                        st.warning("⚠️ Your input contains unsafe or toxic content. Please modify your text.")
                    else:
                        st.error("❌ Something went wrong while generating audio.")

# --- Mode 2: Speech to Text ---
else:
    st.header("Speech to Text")
    st.info("Using Faster-Whisper for accurate transcription.")

    uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3", "wav", "m4a", "flac"])
    
    if uploaded_file:
        st.audio(uploaded_file)

        if st.button("Transcribe Audio"):
            with st.spinner("Transcribing..."):
                try:
                    wrapped_file = StreamlitFileWrapper(uploaded_file)
                    result = speech_to_text(wrapped_file)

                    if result["status"] == "success":
                        st.subheader("Transcription:")
                        st.write(result["text"])

                        st.download_button("Download Text", result["text"], file_name="transcription.txt")

                    else:
                        st.error(f"❌ Error: {result['message']}")

                except Exception as e:
                    error_msg = str(e)

                    if "Unsafe content" in error_msg:
                        st.warning("⚠️ Your input contains unsafe or toxic content. Please modify your audio file.")
                    else:
                        st.error(f"❌ Something went wrong during transcription, {error_msg}")

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.caption("Powered by Bark and Faster-Whisper")
