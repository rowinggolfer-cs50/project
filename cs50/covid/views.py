'''
views.py for cs50 project covid app
'''

from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "covid/index.html"
