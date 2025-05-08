from django.urls import path
from . import views

urlpatterns = [
    path('toggle/<int:blog_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('my/', views.my_bookmarks, name='my_bookmarks'),
]
