# Voicemail Transcriber

A simple web application that transcribes MP3 voicemail files to text using speech recognition technology, with features for metadata management and transcription history.

## Features

- MP3 voicemail file transcription
- Audio playback support
- Metadata capture (caller, address, phone, notes)
- Transcription history management
- Export transcriptions as text files
- Clean and intuitive user interface

## Requirements

- Python 3.13 or higher
- Required packages:
  - ffmpeg-python (>=0.2.0)
  - pydub (>=0.25.1)
  - speechrecognition (>=3.14.2)
  - streamlit (for web interface)
- External dependencies:
  - Google Speech Recognition API (requires internet connection)
  - ffmpeg (for audio conversion)

## Usage

1. Upload an MP3 file using the file uploader
2. Click "Transcribe Audio" to process the voicemail
3. Fill in the metadata form (caller, address, phone, notes)
4. Save the transcription to add it to your history
5. Access saved transcriptions in the sidebar
6. Download transcriptions as text files for record keeping

## How It Works

The application:

1. Accepts MP3 file uploads
2. Provides audio playback functionality
3. Converts MP3 to WAV format temporarily
4. Uses Google Speech Recognition API for transcription
5. Captures and stores metadata with transcriptions
6. Maintains a history of all transcriptions
7. Enables text file exports of transcriptions with metadata
8. Automatically cleans up temporary files
