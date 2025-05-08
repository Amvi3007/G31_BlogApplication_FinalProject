from django.shortcuts import render, get_object_or_404, redirect
from .models import Bookmark
from FunctionalityApp.models import Blog
from django.contrib.auth.decorators import login_required

@login_required
def toggle_bookmark(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, blog=blog)

    if not created:
        bookmark.delete()

    return redirect('dashboard')  


@login_required
def my_bookmarks(request):
    # Filter bookmarks by the currently logged-in user
    bookmarks = Bookmark.objects.filter(user=request.user)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        bookmarks = bookmarks.filter(blog__title__icontains=search_query)

    # Filter functionality
    category_filter = request.GET.get('category', '')
    if category_filter:
        bookmarks = bookmarks.filter(blog__category=category_filter)

    context = {
        'bookmarks': bookmarks,
    }
    
    return render(request, 'my_bookmarks.html', context)

