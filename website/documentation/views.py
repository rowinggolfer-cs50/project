from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "documentation/index.html"


class VenvView(TemplateView):
    template_name = "documentation/venv.html"


class DjangoInstallView(TemplateView):
    template_name = "documentation/install_django.html"


class DjangoStartView(TemplateView):
    template_name = "documentation/create_website.html"


class Sqlite3View(TemplateView):
    template_name = "documentation/django_database.html"


class RunserverView(TemplateView):
    template_name = "documentation/test_server.html"


class SecurityView(TemplateView):
    template_name = "documentation/django_security.html"


class IndexAppView(TemplateView):
    template_name = "documentation/django_apps.html"
