from django import urls
from django.contrib.auth import mixins, login, authenticate
from django.shortcuts import render, redirect   
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from . import models, forms

# Create your views here.
class UserView(mixins.LoginRequiredMixin, generic.DetailView):

    template_name = 'users/user.html'
    model = models.User

    def get_object(self, queryset=None):
        return self.request.user


def register(request):

    if request.method == 'POST':
        form = forms.UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('login')
    else:
        form = forms.UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


class VerificationView(mixins.LoginRequiredMixin, generic.FormView):

    template_name = 'users/verify.html'
    form_class = forms.VerificationForm
    success_url = urls.reverse_lazy('task-list')

    def form_valid(self, form):
        user = self.request.user
        user.verified = True
        user.save()
        return super().form_valid(form)