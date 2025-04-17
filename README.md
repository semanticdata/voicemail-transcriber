# Voicemail Transcriber

A simple web application that transcribes MP3 voicemail files to text using speech recognition technology.

## Requirements

- Python 3.13 or higher
- Required packages:
  - ffmpeg-python (>=0.2.0)
  - pydub (>=0.25.1)
  - speechrecognition (>=3.14.2)
  - streamlit (for web interface)

## Installation

1. Clone the repository
2. Install dependencies:

   ```bash
   pip install .
   ```

## Usage

1. Start the application:

   ```bash
   streamlit run main.py
   ```

2. Open your web browser and navigate to the provided URL
3. Upload an MP3 file using the file uploader
4. Wait for the transcription process to complete
5. View the transcribed text

## How It Works

The application:

1. Accepts MP3 file uploads
2. Converts MP3 to WAV format temporarily
3. Uses Google Speech Recognition API for transcription
4. Displays the transcribed text
5. Automatically cleans up temporary files

## Note

Internet connection is required for the speech recognition service to work.
