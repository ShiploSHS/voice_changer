import io

from django.http import FileResponse, JsonResponse
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import convert_voice_audio, load_active_profile, save_voice_profile
from .serializers import AudioUploadSerializer, VoiceProfileUploadSerializer

def api_root(request):
    return JsonResponse({
        'message': 'Voice Cloner REST API',
        'endpoints': {
            'convert': '/api/convert/',
            'profile': '/api/profile/',
            'profile_active': '/api/profile/active/',
            'admin': '/admin/'
        },
        'convert': {
            'method': 'POST',
            'content_type': 'multipart/form-data',
            'field': 'audio',
            'response_type': 'audio/wav',
            'transcription_header': 'X-Transcription'
        },
        'documentation': 'Import postman_collection.json and POST audio to /api/convert/'
    })


class ConvertAudioView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = AudioUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        audio_file = serializer.validated_data['audio']

        try:
            transcription, output_bytes = convert_voice_audio(audio_file)
        except Exception as exc:
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = FileResponse(
            io.BytesIO(output_bytes),
            content_type='audio/wav',
            filename='converted_voice.wav',
        )
        response['X-Transcription'] = transcription
        return response


class UploadVoiceProfileView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = VoiceProfileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        audio_file = serializer.validated_data['audio']
        profile_name = serializer.validated_data['profile_name']
        preferred_tts_voice = serializer.validated_data.get('preferred_tts_voice')

        try:
            profile_data = save_voice_profile(profile_name, audio_file, preferred_tts_voice)
        except Exception as exc:
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(profile_data, status=status.HTTP_201_CREATED)


class ActiveVoiceProfileView(APIView):
    def get(self, request):
        profile_data = load_active_profile()
        if not profile_data:
            return Response(
                {'detail': 'No active voice profile found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(profile_data)
