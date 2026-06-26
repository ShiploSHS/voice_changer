import io
import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pyttsx3
import torch
from django.conf import settings
from faster_whisper import WhisperModel
from pydub import AudioSegment

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

WHISPER_MODEL = WhisperModel(
    'small',
    device=DEVICE,
    compute_type='float16' if DEVICE == 'cuda' else 'int8',
)

VOICE_PROFILE_DIR = Path(__file__).resolve().parent.parent / 'voice_profiles'
ACTIVE_PROFILE_PATH = VOICE_PROFILE_DIR / 'active_profile.json'


def _ensure_profile_dir():
    VOICE_PROFILE_DIR.mkdir(parents=True, exist_ok=True)


def _load_active_profile():
    if not ACTIVE_PROFILE_PATH.exists():
        return None

    with open(ACTIVE_PROFILE_PATH, 'r', encoding='utf-8') as profile_file:
        return json.load(profile_file)


def _save_active_profile(profile_data):
    _ensure_profile_dir()
    with open(ACTIVE_PROFILE_PATH, 'w', encoding='utf-8') as profile_file:
        json.dump(profile_data, profile_file, indent=2)


def load_active_profile():
    return _load_active_profile()


def _train_voice_profile(profile_name, profile_path):
    _ensure_profile_dir()
    trained_model_path = VOICE_PROFILE_DIR / f'{profile_name}.model'
    metadata = {
        'profile_name': profile_name,
        'sample_path': str(profile_path),
        'trained_at': datetime.utcnow().isoformat() + 'Z',
    }
    with open(trained_model_path, 'w', encoding='utf-8') as model_file:
        json.dump(metadata, model_file, indent=2)
    return trained_model_path


def save_voice_profile(profile_name, uploaded_file, preferred_tts_voice=None):
    wav_path = _convert_to_wav(uploaded_file)
    try:
        _ensure_profile_dir()
        profile_path = VOICE_PROFILE_DIR / f'{profile_name}.wav'
        shutil.copyfile(wav_path, profile_path)
        _train_voice_profile(profile_name, profile_path)

        profile_data = {
            'profile_name': profile_name,
            'sample_path': str(profile_path),
            'preferred_tts_voice': preferred_tts_voice,
            'trained_model_path': str(VOICE_PROFILE_DIR / f'{profile_name}.model'),
            'created_at': datetime.utcnow().isoformat() + 'Z',
        }
        _save_active_profile(profile_data)
        return profile_data
    finally:
        try:
            os.remove(wav_path)
        except OSError:
            pass


def _get_active_profile_voice_name():
    profile = _load_active_profile()
    if profile and profile.get('preferred_tts_voice'):
        return profile.get('preferred_tts_voice')
    return None


def _get_tts_voice_id(engine):
    voice_name = getattr(settings, 'TTS_VOICE', None) or _get_active_profile_voice_name()
    if not voice_name:
        return None

    for voice in engine.getProperty('voices'):
        if voice_name.lower() in (voice.name or '').lower() or voice_name.lower() in (voice.id or '').lower():
            return voice.id
    return None


def _convert_to_wav(file_obj):
    audio = AudioSegment.from_file(file_obj)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        audio.export(tmp.name, format='wav')
        return tmp.name


def _synthesize_text_to_wav(text, output_path):
    engine = pyttsx3.init()
    engine.setProperty('rate', getattr(settings, 'TTS_RATE', 150))

    voice_id = _get_tts_voice_id(engine)
    if voice_id is not None:
        engine.setProperty('voice', voice_id)

    engine.save_to_file(text, output_path)
    engine.runAndWait()


def convert_voice_audio(uploaded_file):
    wav_path = _convert_to_wav(uploaded_file)
    output_path = None
    try:
        result = WHISPER_MODEL.transcribe(wav_path, beam_size=5, language='en')
        segments, _ = result
        transcription = ''.join(segment.text for segment in segments).strip()
        if not transcription:
            raise ValueError('No speech detected in the provided audio.')

        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as out_file:
            output_path = out_file.name

        _synthesize_text_to_wav(transcription, output_path)

        with open(output_path, 'rb') as result_file:
            output_bytes = result_file.read()

        return transcription, output_bytes
    finally:
        for file_path in (wav_path, output_path):
            if file_path:
                try:
                    os.remove(file_path)
                except OSError:
                    pass
