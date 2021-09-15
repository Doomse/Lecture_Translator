from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.TaskListView.as_view(), name='task-list'),
    path('create/', views.TaskCreateView.as_view(), name='task-create'),
    path('detail/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail')
]