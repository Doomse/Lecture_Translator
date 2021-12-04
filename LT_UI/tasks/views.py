from django import http, urls
from django.core.exceptions import BadRequest
from django.core.files.base import ContentFile
from django.http.response import HttpResponse
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


class TaskCreateView(VerifiedMixin, generic.CreateView):

    model = models.Task
    form_class = forms.TaskFilesForm

    def get_success_url(self):
        return urls.reverse('task-translations', args=(self.object.id, ))

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class TaskTranslationView(VerifiedMixin, generic.UpdateView):

    model = models.Task
    form_class = forms.TaskTranslationForm

    def get_success_url(self):
        return urls.reverse('task-list')

    def form_valid(self, form):
        form.instance.status = form.instance.WAIT
        return super().form_valid(form)


#TODO doesn't work due to task remodelling
class TaskDownloadSourceView(VerifiedMixin, generic.DetailView):

    model = models.Task

    def get_object(self, queryset=None):
        return super().get_object(queryset=models.Task.objects.filter(owner=self.request.user))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return http.FileResponse(instance.source.open('rb'), as_attachment=True)


#TODO doesn't work due to task remodelling
class TaskDownloadResultView(VerifiedMixin, generic.DetailView):

    model = models.Task

    def get_object(self, queryset=None):
        return super().get_object(queryset=models.Task.objects.filter(owner=self.request.user))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return http.FileResponse(instance.result.open('rb'), as_attachment=True)


#TODO doesn't work due to task remodelling
class TaskDownloadLogView(VerifiedMixin, generic.DetailView):

    model = models.Task

    def get_object(self, queryset=None):
        return super().get_object(queryset=models.Task.objects.filter(owner=self.request.user))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return http.FileResponse(instance.log.open('rb'), as_attachment=True)


class TaskDownloadResourcesView(VerifiedMixin, generic.DetailView):

    model = models.Task

    def get_object(self, queryset=None):
        return super().get_object(queryset=models.Task.objects.filter(owner=self.request.user))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return http.FileResponse(instance.edit_resources.open('rb'), as_attachment=True)


class TaskReturnView(VerifiedMixin, generic.FormView):

    template_name = 'tasks/task_return.html'
    form_class = forms.TaskReturnForm
    success_url = urls.reverse_lazy('task-list')

    def form_valid(self, form) -> HttpResponse:
        f = form.cleaned_data['cfile']
        content = f.read()
        for line in map(bytes.decode, content.splitlines()):
            if line.startswith('NOTE'):
                id = int(line.split()[1])  # [0] is 'NOTE'
                if not models.SubTask.objects.filter(id=id).exists():
                    raise BadRequest("Could not match correction to any task")
                subtask = models.SubTask.objects.get(id=id)
                # save the file
                subtask.correction.save('correction.vtt', ContentFile(content))
                # if this worked, mark as finished
                subtask.finished = True
                # save again
                subtask.save()
                return super().form_valid(form)  # only the first NOTE in the File should be considered
        raise BadRequest("No task id provided in the file")
        
