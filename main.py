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
st.markdown("Upload an MP3 or WAV file to **play** and **transcribe** it.")

# ----------------------------
# Utility Functions
# ----------------------------


@st.cache_data
def transcribe_audio(audio_path: str, file_type: str) -> str:
    recognizer = sr.Recognizer()

    try:
        st.write(f"Processing audio file: {audio_path}")

        try:
            # Load the audio file based on detected type
            if file_type == "mp3":
                audio = AudioSegment.from_mp3(audio_path)
                st.write("Successfully loaded MP3 file")
            else:
                # Try loading WAV with explicit codec first
                try:
                    audio = AudioSegment.from_file(
                        audio_path, format="wav", codec="adpcm_ms"
                    )
                except:
                    # Fallback to default WAV loading if not ADPCM
                    audio = AudioSegment.from_wav(audio_path)
                st.write("Successfully loaded WAV file")
        except Exception as e:
            st.error(f"Error loading audio file: {str(e)}")
            return f"❗ Error loading audio file: {str(e)}"

        # Create temporary WAV file for speech recognition
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            wav_path = temp_wav.name
            st.write(f"Converting to WAV format: {wav_path}")

            try:
                # Normalize audio format before export
                audio = audio.set_channels(1)  # Convert to mono
                audio = audio.set_frame_rate(44100)  # Set sample rate

                # Export with explicit codec and format settings
                audio.export(
                    wav_path,
                    format="wav",
                    codec="pcm_s16le",  # Standard 16-bit PCM codec
                    parameters=[
                        "-ar",
                        "44100",  # Standard sample rate
                        "-ac",
                        "1",  # Mono
                    ],
                )
                st.write("Successfully converted and exported audio")
            except Exception as e:
                st.error(f"Error during audio conversion: {str(e)}")
                if os.path.exists(wav_path):
                    os.remove(wav_path)
                return f"❗ Error during audio conversion: {str(e)}"

            # Verify the converted file
            if not os.path.exists(wav_path):
                return "❗ Failed to create WAV file"

            if os.path.getsize(wav_path) == 0:
                os.remove(wav_path)
                return "❗ Generated WAV file is empty"

            st.write("Starting transcription...")
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                st.write("Transcription completed successfully")
                return text
    except sr.UnknownValueError:
        return "❗ Speech recognition could not understand the audio."
    except sr.RequestError as e:
        return f"❗ Could not request results from the recognition service: {e}"
    except Exception as e:
        st.error(f"Unexpected error during processing: {str(e)}")
        return f"❗ Error processing audio: {str(e)}"
    finally:
        # Clean up temporary files
        if "wav_path" in locals() and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception as e:
                st.error(f"Error cleaning up temporary file: {str(e)}")


def save_uploaded_file(uploaded_file) -> tuple[str, str]:
    """Save uploaded file and detect its true type. Returns (path, detected_type)"""
    # First save the file with its original extension
    extension = ".mp3" if uploaded_file.type == "audio/mp3" else ".wav"
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_path = temp_file.name

    # Try to detect the true file type
    try:
        # Try loading as MP3 first
        AudioSegment.from_mp3(temp_path)
        return temp_path, "mp3"
    except:
        try:
            # If MP3 fails, try as WAV
            audio = AudioSegment.from_file(temp_path, format="wav", codec="adpcm_ms")
            # Convert to standard WAV format immediately to avoid encoding issues
            with tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False
            ) as standard_wav:
                audio.export(
                    standard_wav.name,
                    format="wav",
                    codec="pcm_s16le",  # Use standard PCM encoding
                    parameters=[
                        "-ar",
                        "44100",  # Set sample rate
                        "-ac",
                        "1",  # Convert to mono
                    ],
                )
                os.remove(temp_path)  # Remove the original file
                return standard_wav.name, "wav"
        except Exception as e:
            st.error(f"Error processing WAV file: {str(e)}")
            # If both fail, default to the original type
            return temp_path, "mp3" if uploaded_file.type == "audio/mp3" else "wav"


# ----------------------------
# Session State Initialization
# ----------------------------

st.session_state.setdefault("transcription_history", [])
st.session_state.setdefault("current_transcription", None)

# ----------------------------
# File Upload + Transcription
# ----------------------------

uploaded_file = st.file_uploader("Upload MP3 or WAV", type=["mp3", "wav"])

if uploaded_file:
    st.audio(uploaded_file, format=uploaded_file.type)

    if st.button("📝 Transcribe Audio"):
        with st.spinner("Transcribing..."):
            try:
                audio_path, detected_type = save_uploaded_file(uploaded_file)
                st.session_state.current_transcription = transcribe_audio(
                    audio_path, detected_type
                )
            except Exception as e:
                st.error(f"Unexpected error: {e}")
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)

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


def export_transcription(entry: dict) -> str:
    timestamp = entry["timestamp"].replace(":", "-")
    caller = entry.get("caller", "Unknown")
    filename = f"{timestamp}_{caller}.txt"

    content = [
        f"Voicemail Transcription Export",
        f"============================",
        f"",
        f"Caller: {entry.get('caller', '—')}",
        f"Address: {entry.get('address', '—')}",
        f"Phone: {entry.get('phone', '—')}",
        f"Timestamp: {entry['timestamp']}",
        f"Filename: {entry['filename']}",
        f"",
        f"Notes:",
        f"{entry.get('note', '—')}",
        f"",
        f"Transcription:",
        f"{entry['transcription']}",
    ]

    return "\n".join(content)


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

            timestamp = entry["timestamp"].replace(":", "-")
            caller = entry.get("caller", "Unknown")
            filename = f"{timestamp}_{caller}.txt"
            content = export_transcription(entry)
            st.download_button(
                "📥 Download TXT",
                data=content,
                file_name=filename,
                mime="text/plain",
                key=f"download_{entry['timestamp']}",
            )

    if st.sidebar.button("🗑️ Clear History"):
        st.session_state.transcription_history.clear()
        st.rerun()
else:
    st.sidebar.write("No transcriptions yet.")
