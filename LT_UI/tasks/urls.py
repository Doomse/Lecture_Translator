from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.TaskListView.as_view(), name='task-list'),
    path('create/', views.TaskCreateView.as_view(), name='task-create'),
    path('download/<int:pk>/source/', views.TaskDownloadSourceView.as_view(), name='task-download-source'),
    path('download/<int:pk>/result/', views.TaskDownloadResultView.as_view(), name='task-download-result'),
    path('translations/<int:pk>/', views.TaskTranslationView.as_view(), name='task-translations'),
]