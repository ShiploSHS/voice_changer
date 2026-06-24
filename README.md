# Voice Cloner REST API

This repository contains a Django REST API backend for a voice cloning / voice changing service.

## What it does

- Accepts a recorded audio file via an HTTP `POST` request
- Uses an open source speech transcription model to read the spoken text
- Generates the same text using an open source TTS model in a synthetic voice
- Returns a WAV file response and the transcription in a response header

## Project structure

- `manage.py` - Django CLI entrypoint
- `voiceapi/` - Django project configuration
- `converter/` - app containing the API endpoint and voice conversion service

## API endpoint

- `POST /api/convert/`
- Form field: `audio` (multipart file upload)
- Returns: `audio/wav` file named `converted_voice.wav`
- Response header: `X-Transcription` with detected text

## Setup

1. Install dependencies with Pipenv:
   ```powershell
   pipenv install
   pipenv shell
   ```
2. Install system dependency:
   - `ffmpeg` must be installed and available on `PATH`

3. Run migrations:
   ```powershell
   python manage.py migrate
   ```
4. Run the development server:
   ```powershell
   python manage.py runserver
   ```

## Postman testing

Import `postman_collection.json` into Postman and set the variables:

- `base_url`: `http://127.0.0.1:8000`
- `audio_file_path`: path to a local WAV or MP3 audio file

Send a `POST` request to `/api/convert/` with the form field `audio`.

The root URL `/` now returns a small API info JSON response with:

- `convert.method`
- `convert.content_type`
- `convert.field`
- `convert.response_type`
- `convert.transcription_header`

## GPU acceleration

The service automatically uses CUDA if `torch.cuda.is_available()` returns `True`.

## Notes

- The current implementation uses `faster-whisper` for transcription and `pyttsx3` for offline speech synthesis.
- This is a clean, modular backend implementation suitable for a REST API.
- To improve voice quality later, switch `pyttsx3` to a model-based TTS library.
