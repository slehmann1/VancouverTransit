from django.urls import path

from . import views

urlpatterns = [
    path('transit', views.Map.as_view(), name='map'),
]