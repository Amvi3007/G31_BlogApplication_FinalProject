# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
   # Category selection page
    path('forum/', views.select_category, name='select_category'),
    
    # Action selection page for each category
    path('forum/<str:category>/', views.select_action, name='select_action'),
    
    # Category form for GET, POST, PUT, DELETE actions
    path('forum/<str:category>/<str:action>/', views.category_form, name='category_form'),
    
    # Routes for updating an entry
    path('forum/<str:category>/update/<int:entry_id>/', views.category_form, {'action': 'put'}, name='update_entry'),
    
    # Routes for deleting an entry
    path('forum/<str:category>/delete/<int:entry_id>/', views.category_form, {'action': 'delete'}, name='delete_entry'),

    path('forum/<str:category>/<str:action>/', views.select_action, name='category_action'),
]
