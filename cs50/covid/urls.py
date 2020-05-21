'''
urls.py for my cs50 covid django-app
'''
from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name="covid-homepage"),
]
