from django.urls import path
from . import views

urlpatterns = [
    path('createblog/', views.add_blog_view, name='create_blog'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('view/<int:blog_id>/', views.view_blog, name='view_blog'),
    path('like/<int:blog_id>/', views.like_blog, name='like_blog'),
    path('comment/<int:blog_id>/', views.comment_blog, name='comment_blog'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('edit/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('delete/<int:blog_id>/', views.delete_blog, name='delete_blog'),
    path('profile/', views.profile_view, name='profile'),
    path('my-blogs/', views.user_blogs, name='my_blogs'),
    path('about/',views.about,name = 'about'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('thank-you/', views.thank_you, name='thank_you'),
]
