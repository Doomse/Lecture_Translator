from django import forms, urls
from django.shortcuts import render
from django.contrib.auth import mixins
from django.views import generic
from . import models

# Create your views here.
class UserView(mixins.LoginRequiredMixin, generic.DetailView):

    template_name = 'users/user.html'
    model = models.User

    def get_object(self, queryset=None):
        return self.request.user