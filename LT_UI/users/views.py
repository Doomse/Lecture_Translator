from django import urls
from django.contrib.auth import mixins
from django.views import generic
from . import models, forms

# Create your views here.
class UserView(mixins.LoginRequiredMixin, generic.DetailView):

    template_name = 'users/user.html'
    model = models.User

    def get_object(self, queryset=None):
        return self.request.user


class VerificationView(mixins.LoginRequiredMixin, generic.FormView):

    template_name = 'users/verify.html'
    form_class = forms.VerificationForm
    success_url = urls.reverse_lazy('task-list')

    def form_valid(self, form):
        user = self.request.user
        user.verified = True
        user.save()
        return super().form_valid(form)