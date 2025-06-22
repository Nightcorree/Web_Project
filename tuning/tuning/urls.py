from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 
from atelier.views_api import CustomRegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('atelier.urls_api')),
    path('api/v1/auth/', include('dj_rest_auth.urls')), 
    path('api/v1/auth/registration/', CustomRegisterView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)