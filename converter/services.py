import io
import os
import tempfile

import pyttsx3
import torch
from faster_whisper import WhisperModel
from pydub import AudioSegment

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

WHISPER_MODEL = WhisperModel(
    'small',
    device=DEVICE,
    compute_type='float16' if DEVICE == 'cuda' else 'int8',
)


def _convert_to_wav(file_obj):
    audio = AudioSegment.from_file(file_obj)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        audio.export(tmp.name, format='wav')
        return tmp.name


def _synthesize_text_to_wav(text, output_path):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[0].id)
    engine.save_to_file(text, output_path)
    engine.runAndWait()


def convert_voice_audio(uploaded_file):
    wav_path = _convert_to_wav(uploaded_file)
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
            try:
                os.remove(file_path)
            except OSError:
                pass
