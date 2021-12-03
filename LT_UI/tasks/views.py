from django import http, urls
from django.views import generic
from django.contrib.auth import mixins
from . import models, forms


class VerifiedMixin(mixins.UserPassesTestMixin):

    def test_func(self):
        return self.request.user.verified

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return http.HttpResponseRedirect(urls.reverse('verify'))
        return super().handle_no_permission()


class TaskListView(VerifiedMixin, generic.ListView):

    def get_queryset(self):
        return models.Task.objects.filter(owner=self.request.user)


class TaskZipCreateView(VerifiedMixin, generic.CreateView):

    model = models.Task
    form_class = forms.TaskZipForm

    def get_success_url(self):
        return urls.reverse('task-translations', args=(self.object.id, ))

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class TaskFilesCreateView(TaskZipCreateView):

    form_class = forms.TaskFilesForm


class TaskTranslationView(VerifiedMixin, generic.UpdateView):

    model = models.Task
    form_class = forms.TaskTranslationForm

    def get_success_url(self):
        return urls.reverse('task-list')

    def form_valid(self, form):
        form.instance.status = form.instance.WAIT
        return super().form_valid(form)


class TaskDownloadSourceView(VerifiedMixin, generic.DetailView):

    model = models.Task

    def get_object(self, queryset=None):
        return super().get_object(queryset=models.Task.objects.filter(owner=self.request.user))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return http.FileResponse(instance.source.open('rb'), as_attachment=True)


class TaskDownloadResultView(VerifiedMixin, generic.DetailView):

    model = models.Task

    def get_object(self, queryset=None):
        return super().get_object(queryset=models.Task.objects.filter(owner=self.request.user))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return http.FileResponse(instance.result.open('rb'), as_attachment=True)


class TaskDownloadLogView(VerifiedMixin, generic.DetailView):

    model = models.Task

    def get_object(self, queryset=None):
        return super().get_object(queryset=models.Task.objects.filter(owner=self.request.user))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return http.FileResponse(instance.log.open('rb'), as_attachment=True)