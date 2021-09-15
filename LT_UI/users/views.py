from django import forms, urls
from django.shortcuts import render
#from django.contrib.messages import views as message_views
from django.contrib.auth import mixins
from django.views import generic
from . import models, forms

# Create your views here.
class UserView(mixins.LoginRequiredMixin, generic.DetailView):

    template_name = 'users/user.html'
    model = models.User

    def get_object(self, queryset=None):
        return self.request.user


#class RegisterView(message_views.SuccessMessageMixin, generic.CreateView):
    
#    template_name = 'users/register.html'
#    success_url = urls.reverse_lazy('login')
#    form_class = forms.UserRegisterForm
#    success_message = "Your account was created successfully"