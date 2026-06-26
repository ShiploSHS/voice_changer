from rest_framework import serializers


class AudioUploadSerializer(serializers.Serializer):
    audio = serializers.FileField(required=True)


class VoiceProfileUploadSerializer(serializers.Serializer):
    profile_name = serializers.CharField(max_length=128, required=True)
    audio = serializers.FileField(required=True)
    preferred_tts_voice = serializers.CharField(required=False, allow_blank=True)
