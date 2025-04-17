import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os


def transcribe_audio(audio_file):
    # Create a recognizer instance
    recognizer = sr.Recognizer()

    # Convert MP3 to WAV using pydub
    audio = AudioSegment.from_mp3(audio_file)

    wav_path = None
    try:
        # Export as WAV to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            wav_path = temp_wav.name
            audio.export(wav_path, format="wav")

        # Use speech recognition on the WAV file
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                return "Speech recognition could not understand the audio"
            except sr.RequestError as e:
                return f"Could not request results from speech recognition service; {str(e)}"
    finally:
        # Clean up temporary file
        if wav_path and os.path.exists(wav_path):
            try:
                os.unlink(wav_path)
            except Exception:
                pass


# Streamlit UI
st.title("Voicemail Transcriber")
st.write("Upload an MP3 file to get its transcription")

# File uploader
uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

if uploaded_file is not None:
    mp3_path = None
    try:
        # Create a temporary file to save the uploaded MP3
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3:
            mp3_path = temp_mp3.name
            temp_mp3.write(uploaded_file.getvalue())

        with st.spinner("Transcribing..."):
            # Get transcription
            transcription = transcribe_audio(mp3_path)

            # Display results
            st.subheader("Transcription Result:")
            st.write(transcription)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        # Clean up temporary file
        if mp3_path and os.path.exists(mp3_path):
            try:
                os.unlink(mp3_path)
            except Exception:
                pass
