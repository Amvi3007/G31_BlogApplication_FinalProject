from django.urls import path
from . import views

# AuthApp/urls.py
app_name = 'AuthApp'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
]

