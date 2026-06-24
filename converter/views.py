import io

from django.http import FileResponse, JsonResponse
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import convert_voice_audio
from .serializers import AudioUploadSerializer

def api_root(request):
    return JsonResponse({
        'message': 'Voice Cloner REST API',
        'endpoints': {
            'convert': '/api/convert/',
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
