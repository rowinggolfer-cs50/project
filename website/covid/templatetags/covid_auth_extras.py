from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name="has_covid_write_perms")
def has_covid_write__perms(user):
    try:
        group = Group.objects.get(name="covid-write-permission")
        return group in user.groups.all()
    except Group.DoesNotExist:
        pass
    return False
