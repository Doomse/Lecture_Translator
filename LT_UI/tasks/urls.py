from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.TaskListView.as_view(), name='task-list'),
    path('create/zip/', views.TaskZipCreateView.as_view(), name='task-create-zip'),
    path('create/files/', views.TaskFilesCreateView.as_view(), name='task-create-files'),
    path('download/<int:pk>/source/', views.TaskDownloadSourceView.as_view(), name='task-download-source'),
    path('download/<int:pk>/result/', views.TaskDownloadResultView.as_view(), name='task-download-result'),
    path('download/<int:pk>/log/', views.TaskDownloadLogView.as_view(), name='task-download-log'),
    path('translations/<int:pk>/', views.TaskTranslationView.as_view(), name='task-translations'),
]