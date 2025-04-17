import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
from datetime import datetime

# ----------------------------
# Configuration
# ----------------------------

st.set_page_config(
    page_title="Voicemail Transcriber", page_icon="🎤", layout="centered"
)

st.title("🎤 Voicemail Transcriber")
st.markdown("Upload an MP3 file to **play** and **transcribe** it.")

# ----------------------------
# Utility Functions
# ----------------------------


@st.cache_data
def transcribe_audio(mp3_path: str) -> str:
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_mp3(mp3_path)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
        wav_path = temp_wav.name
        audio.export(wav_path, format="wav")

    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "❗ Speech recognition could not understand the audio."
    except sr.RequestError as e:
        return f"❗ Could not request results from the recognition service: {e}"
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


def save_uploaded_file(uploaded_file) -> str:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        return temp_file.name


# ----------------------------
# Session State Initialization
# ----------------------------

st.session_state.setdefault("transcription_history", [])
st.session_state.setdefault("current_transcription", None)

# ----------------------------
# File Upload + Transcription
# ----------------------------

uploaded_file = st.file_uploader("Upload MP3", type=["mp3"])

if uploaded_file:
    st.audio(uploaded_file, format="audio/mp3")

    if st.button("📝 Transcribe Audio"):
        with st.spinner("Transcribing..."):
            try:
                mp3_path = save_uploaded_file(uploaded_file)
                st.session_state.current_transcription = transcribe_audio(mp3_path)
            except Exception as e:
                st.error(f"Unexpected error: {e}")
            finally:
                if os.path.exists(mp3_path):
                    os.remove(mp3_path)

# ----------------------------
# Metadata Form
# ----------------------------

if st.session_state.current_transcription:
    with st.form("metadata_form"):
        st.subheader("🗂️ Transcription Metadata")
        caller = st.text_input("Caller", placeholder="E.g., John Doe")
        address = st.text_input(
            "Address", placeholder="E.g., 4141 Douglas Dr N, Crystal"
        )
        phone = st.text_input("Phone", placeholder="E.g., 'Call from Resident'")
        note = st.text_area("Notes", placeholder="Optional notes...")

        st.subheader("🧾 Transcription Output")
        st.write(st.session_state.current_transcription)

        if st.form_submit_button("💾 Save Transcription"):
            st.session_state.transcription_history.append(
                {
                    "filename": uploaded_file.name,
                    "address": address,
                    "phone": phone,
                    "note": note,
                    "caller": caller,
                    "transcription": st.session_state.current_transcription,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            st.session_state.current_transcription = None
            st.success("✅ Transcription saved successfully.")
            st.rerun()

# ----------------------------
# Sidebar: History Display
# ----------------------------

st.sidebar.title("🕘 Transcription History")

if st.session_state.transcription_history:
    for entry in reversed(st.session_state.transcription_history):
        label = entry.get("address") or entry["filename"]
        with st.sidebar.expander(f"📝 {label}"):
            st.markdown(f"**Caller:** {entry.get('caller', '—')}")
            st.markdown(f"**Address:** {entry.get('address', '—')}")
            st.markdown(f"**Phone:** {entry.get('phone', '—')}")
            if entry.get("note"):
                st.markdown(f"**Notes:** {entry['note']}")
            st.markdown(f"**Timestamp:** {entry['timestamp']}")
            st.markdown("**Transcription:**")
            st.write(entry["transcription"])

    if st.sidebar.button("🗑️ Clear History"):
        st.session_state.transcription_history.clear()
        st.rerun()
else:
    st.sidebar.write("No transcriptions yet.")
