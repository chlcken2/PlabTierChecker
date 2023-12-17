from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('plabtiercheck_app.urls')),
    path('accounts/', include('allauth.urls')),  # allauth URL 패턴 추가
]
