from django.urls import path, re_path

from documentation import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="documentation-homepage"),
    path(
        "create-venv",
        views.VenvView.as_view(),
        name="documentation-create-venv",
    ),
    path(
        "install-django",
        views.DjangoInstallView.as_view(),
        name="documentation-install-django",
    ),
    path(
        "start-django",
        views.DjangoStartView.as_view(),
        name="documentation-start-django",
    ),
    path(
        "sqlite",
        views.Sqlite3View.as_view(),
        name="documentation-sqlite",
    ),
    path(
        "runserver",
        views.RunserverView.as_view(),
        name="documentation-runserver",
    ),
    path(
        "security",
        views.SecurityView.as_view(),
        name="documentation-security",
    ),
    path(
        "index-app",
        views.IndexAppView.as_view(),
        name="documentation-indexapp",
    ),
]
