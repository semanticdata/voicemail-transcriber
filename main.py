import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
from datetime import datetime


@st.cache_data
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


# Initialize session state for transcription history
if 'transcription_history' not in st.session_state:
    st.session_state.transcription_history = []

# Streamlit UI
st.set_page_config(
    page_title="Voicemail Transcriber",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)
st.title("Voicemail Transcriber")
st.write("Upload an MP3 file to play and transcribe it")

# File uploader
uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

if uploaded_file is not None:
    # Display audio player
    st.audio(uploaded_file)

    # Add transcribe button
    if st.button("Transcribe Audio"):
        mp3_path = None
        try:
            # Create a temporary file to save the uploaded MP3
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3:
                mp3_path = temp_mp3.name
                temp_mp3.write(uploaded_file.getvalue())

            with st.spinner("Transcribing..."):
                # Get transcription
                transcription = transcribe_audio(mp3_path)

                # Add to history
                st.session_state.transcription_history.append({
                    'filename': uploaded_file.name,
                    'transcription': transcription,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

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

# Display transcription history
st.sidebar.title("Transcription History")
if len(st.session_state.transcription_history) > 0:
    if st.sidebar.button("Clear History"):
        st.session_state.transcription_history = []
        st.rerun()
    
    for idx, entry in enumerate(reversed(st.session_state.transcription_history)):
        with st.sidebar.expander(f"📝 {entry['filename']}"):
            st.write(f"**Timestamp:** {entry['timestamp']}")
            st.write(f"**Transcription:**\n{entry['transcription']}")
else:
    st.sidebar.write("No transcriptions yet.")
