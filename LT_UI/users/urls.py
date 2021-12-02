from django.urls import path
from django_cas_ng import views as cas_views
from . import views

urlpatterns = [
    path('', cas_views.LoginView.as_view(), name='cas_ng_login'),
    path('logout/', cas_views.LogoutView.as_view(), name='cas_ng_logout'),
    path('verify/', views.VerificationView.as_view(), name='verify'),
    path('user/', views.UserView.as_view(), name='user'),
]