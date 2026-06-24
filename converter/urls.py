from django.urls import path
from .views import ConvertAudioView

urlpatterns = [
    path('convert/', ConvertAudioView.as_view(), name='convert-audio'),
]
