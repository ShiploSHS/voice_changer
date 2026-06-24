from django.contrib import admin
from django.urls import include, path
from converter.views import api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('converter.urls')),
]
