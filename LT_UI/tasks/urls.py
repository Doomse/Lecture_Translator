from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.TaskListView.as_view(), name='task-list'),
    path('create/files/', views.TaskCreateView.as_view(), name='task-create'),

    #TODO these views are currently broken
    #path('download/<int:pk>/source/', views.TaskDownloadSourceView.as_view(), name='task-download-source'),
    #path('download/<int:pk>/result/', views.TaskDownloadResultView.as_view(), name='task-download-result'),
    #path('download/<int:pk>/log/', views.TaskDownloadLogView.as_view(), name='task-download-log'),

    path('download/<int:pk>/resources/', views.TaskDownloadResourcesView.as_view(), name='task-download-resources'),

    path('translations/<int:pk>/', views.TaskTranslationView.as_view(), name='task-translations'),
    path('return/', views.TaskReturnView.as_view(), name='task-return'),
    path('api/return/', views.TaskReturnAPIView.as_view(), name='task-return-api'),
    path('api/get_update/', views.get_last_update, name='get-task-update'),
]