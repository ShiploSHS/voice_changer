from django.urls import path
from .views import ActiveVoiceProfileView, ConvertAudioView, UploadVoiceProfileView

urlpatterns = [
    path('convert/', ConvertAudioView.as_view(), name='convert-audio'),
    path('profile/', UploadVoiceProfileView.as_view(), name='upload-voice-profile'),
    path('profile/active/', ActiveVoiceProfileView.as_view(), name='active-voice-profile'),
]