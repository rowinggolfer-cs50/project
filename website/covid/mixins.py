#! /usr/bin/python
"""
some mixins to check users have permissions to perform certain actions.
"""
from django.conf import settings

from django.urls import reverse_lazy

from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages

from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):

    """
    A mixin to ensure that user is logged in.
    """

    @method_decorator(login_required(login_url=reverse_lazy("my-login")))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class UserCheckMixin(object):

    """
    A mixin to ensure user has certain attributes.
    """

    mixin_error = ""
    user_check_failure_path = reverse_lazy("covid-help")

    def check_user(self, user):
        return True

    def user_check_failed(self, request, *args, **kwargs):
        if self.mixin_error:
            messages.error(request, self.mixin_error)
        return redirect(self.user_check_failure_path)

    @method_decorator(login_required(login_url=reverse_lazy("my-login")))
    def dispatch(self, request, *args, **kwargs):
        if not self.check_user(request.user):
            return self.user_check_failed(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)


class CovidWriteRecordsMixin(UserCheckMixin):
    """
    A mixin to check user belongs to the group 'covid-write-permissions'
    """

    user_check_failure_path = reverse_lazy("covid-write-permission-help")
    GROUP_NAME = "covid-write-permission"

    def get_initial(self):
        initial = {}
        user = self.request.user
        if user and user.is_authenticated:
            initial["user"] = user
            initial["author"] = user.get_full_name() or user.get_username()
        return initial

    def check_user(self, user):
        try:
            group = Group.objects.get(name=self.GROUP_NAME)
            is_member = group in user.groups.all()
            if not is_member:
                messages.error(
                    self.request,
                    "Sorry, you are not member of group '%s'" % self.GROUP_NAME,
                )
            return is_member
        except Group.DoesNotExist:
            message = "There is no group named %s" % self.GROUP_NAME
            messages.error(self.request, message)
        return False
