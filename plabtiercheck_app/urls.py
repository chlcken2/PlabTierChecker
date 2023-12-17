from django.urls import path, include
from plabtiercheck_app import views

urlpatterns = [
    path('', views.index),
]

