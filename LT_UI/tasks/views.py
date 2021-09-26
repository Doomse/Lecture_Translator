from django import forms, http
from django.views import generic
from django.contrib.auth import mixins
from . import models, forms



class TaskListView(mixins.LoginRequiredMixin, generic.ListView):

    def get_queryset(self):
        return models.Task.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = forms.TaskForm()

        return context


class TaskCreateView(mixins.LoginRequiredMixin, generic.CreateView):

    model = models.Task
    form_class = forms.TaskForm
    success_url = '/tasks/list/'
    template_name_suffix = '_form_wrapper'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class TaskUpdateView(mixins.LoginRequiredMixin, generic.UpdateView):

    model = models.Task
    form_class = forms.TaskForm
    success_url = '/tasks/list/'
    template_name_suffix = '_form_wrapper'


class TaskDetailView(mixins.LoginRequiredMixin, generic.DetailView):

    model = models.Task

    def get_object(self, queryset=None):
        return super().get_object(queryset=models.Task.objects.filter(owner=self.request.user))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return http.FileResponse(instance.source.open('rb'), as_attachment=True)