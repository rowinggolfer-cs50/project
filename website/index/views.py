'''
views.py for cs50 project index app
'''

from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "index.html"
