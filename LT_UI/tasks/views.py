from django import forms, http, urls
from django.views import generic
from django.contrib.auth import mixins
from . import models, forms



class TaskListView(mixins.LoginRequiredMixin, generic.ListView):

    def get_queryset(self):
        return models.Task.objects.filter(owner=self.request.user)


class TaskCreateView(mixins.LoginRequiredMixin, generic.CreateView):

    model = models.Task
    form_class = forms.TaskForm

    def get_success_url(self):
        return urls.reverse('task-translations', args=(self.object.id, ))

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class TaskTranslationView(mixins.LoginRequiredMixin, generic.UpdateView):

    model = models.Task
    form_class = forms.TaskTranslationForm

    def get_success_url(self):
        return urls.reverse('task-list')

    def form_valid(self, form):
        form.instance.status = form.instance.WAIT
        return super().form_valid(form)


class TaskDownloadSourceView(mixins.LoginRequiredMixin, generic.DetailView):

    model = models.Task

    def get_object(self, queryset=None):
        return super().get_object(queryset=models.Task.objects.filter(owner=self.request.user))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return http.FileResponse(instance.source.open('rb'), as_attachment=True)


class TaskDownloadResultView(mixins.LoginRequiredMixin, generic.DetailView):

    model = models.Task

    def get_object(self, queryset=None):
        return super().get_object(queryset=models.Task.objects.filter(owner=self.request.user))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return http.FileResponse(instance.result.open('rb'), as_attachment=True)