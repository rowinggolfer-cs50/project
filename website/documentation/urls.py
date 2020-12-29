from django.urls import path, re_path

from documentation import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="documentation-homepage"),
]
