from django import http
from django.views import generic
from django.contrib.auth import mixins
from . import models



class TaskListView(mixins.LoginRequiredMixin, generic.ListView):

    def get_queryset(self):
        return models.Task.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form_html'] = TaskInlineCreateView.as_view()(self.request, **kwargs).rendered_content

        return context


class TaskInlineCreateView(mixins.LoginRequiredMixin, generic.CreateView):

    model = models.Task
    fields = ['title', 'source']
    success_url = '/tasks/list/'
    template_name_suffix = '_inline_form'

    def form_invalid(self, form):
        response = super().form_invalid(form)
        print(form.errors)
        return response

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class TaskCreateView(TaskInlineCreateView):

    template_name_suffix = '_form_wrapper'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form_html'] = TaskInlineCreateView.as_view()(self.request, **kwargs).rendered_content

        return context


class TaskDetailView(mixins.LoginRequiredMixin, generic.DetailView):

    model = models.Task

    def get_object(self, queryset=None):
        return super().get_object(queryset=models.Task.objects.filter(owner=self.request.user))

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        return http.FileResponse(instance.source.open('rb'), as_attachment=True)