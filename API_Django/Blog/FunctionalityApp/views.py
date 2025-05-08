from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from FunctionalityApp.models import Blog, Comment
from .forms import BlogForm,ContactForm,FeedbackForm
import requests
from django.db.models import Q  # 👈 required for complex queries (search + filter)
from django.views.decorators.cache import never_cache
from AuthApp.models import Profile  # ✅ Correct import
from django.templatetags.static import static
from django.http import HttpResponse

def add_blog_view(request):
    blogs = Blog.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('upload_image')
        category = request.POST.get('category') 
        author = request.user

        if not title:
            messages.error(request, "Title is mandatory")
        elif not content:
            messages.error(request, "You have not added content")
        else:
            new_blog = Blog.objects.create(
                title=title,
                content=content,
                upload_image=image,
                category=category,
                author=author
            )
            return redirect('view_blog', blog_id=new_blog.blog_id)

    return render(request, 'create_blog.html', context={"Blogs": blogs})

@never_cache
@login_required
def dashboard_view(request):
    blogs = Blog.objects.all()
    categories = ['Food', 'Beauty', 'Politics', 'Travel', 'Lifestyle']

    theme_cards = [
        {"name": "Food", "image": static("images/food2.jpg")},
        {"name": "Travel", "image": static("images/travel2.jpg")},
        {"name": "Beauty", "image": static("images/beauty.jpg")},
        {"name": "Lifestyle", "image": static("images/lifestyle.jpg")},
        {"name": "Politics", "image": static("images/politics.jpg")},
    ]

    search_query = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category', '').strip()

    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    if selected_category:
        blogs = blogs.filter(category__iexact=selected_category)

    # 🔥 Get profile object
    profile = None
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = None

    return render(request, 'home1.html', {
        'Blogs': blogs,
        'categories': categories,
        'theme_cards': theme_cards,
        'profile': profile  # ⬅️ Now available in template
    })


@login_required
def view_blog(request, blog_id):
    blog = get_object_or_404(Blog, blog_id=blog_id)
    comments = blog.comments.all().order_by('-timestamp')
    already_liked = request.user in blog.liked_by.all()

    return render(request, 'view_blog.html', {
        'blog': blog,
        'comments': comments,
        'already_liked': already_liked
    })


@login_required
def like_blog(request, blog_id):
    blog = get_object_or_404(Blog, blog_id=blog_id)
    user = request.user
    if user in blog.liked_by.all():
        return JsonResponse({
            'like_count': blog.liked_by.count(),
            'already_liked': True,
            'message': 'You have already liked this blog.'
        })
    else:
        blog.liked_by.add(user)
        return JsonResponse({
            'like_count': blog.liked_by.count(),
            'already_liked': False,
            'message': 'Thanks for liking the blog!'
        })



@login_required
def comment_blog(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, blog_id=blog_id)
        content = request.POST.get('content')
        if content:
            Comment.objects.create(blog=blog, user=request.user, content=content)
        return redirect('view_blog', blog_id=blog_id)


@login_required
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, blog_id=blog_id)

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('view_blog', blog_id=blog.blog_id)
    else:
        form = BlogForm(instance=blog)

    return render(request, 'edit_blog.html', {'form': form, 'blog': blog})


@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, blog_id=blog_id)
    if request.user != blog.author and not request.user.is_superuser:
        return redirect('dashboard')

    blog.delete()
    return redirect('dashboard')

@login_required
def custom_logout_view(request):
    logout(request)
    return redirect('home')


from AuthApp.models import Profile  # ✅ correct import
from django.core.files.storage import default_storage

@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    # ✅ Handle image upload
    if request.method == "POST" and request.FILES.get('profile_image'):
        profile.image = request.FILES['profile_image']
        profile.save()
        messages.success(request, "Profile image updated successfully!")

    interests_raw = profile.categories or ""
    interests_list = [i.strip().capitalize() for i in interests_raw.split(",") if i.strip()]

    context = {
        'name': user.get_full_name() or user.username,
        'email': user.email,
        'role': "Admin" if user.is_superuser else "User",
        'interests_list': interests_list if not user.is_superuser else None,
        'profile_image': profile.image.url if profile.image else None,
    }

    return render(request, 'profile.html', context)


@login_required
def user_blogs(request):
    selected_category = request.GET.get('category', '').strip()
    search_query = request.GET.get('search', '').strip()

    user_blogs = Blog.objects.filter(author=request.user)

    if selected_category:
        user_blogs = user_blogs.filter(category__iexact=selected_category)

    if search_query:
        user_blogs = user_blogs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    categories = ['Food', 'Beauty', 'Politics', 'Travel', 'Lifestyle']

    return render(request, 'myblogs.html', {
        'blogs': user_blogs,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
    })


def about(request):
    return render(request,'about.html')


def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            data = {
                'feedback_category': form.cleaned_data['feedback_category'],
                'improvement': form.cleaned_data['improvement'],
                'topic_interest': ', '.join(form.cleaned_data['topic_interest']),
                'recommend': 'yes' if form.cleaned_data['recommend'] else 'no',
                'user_experience': form.cleaned_data['user_experience']
            }

            # Send POST request to Flask API
            try:
                response = requests.post('http://127.0.0.1:5000/submit', data=data)
                if response.status_code == 200:
                    return redirect('thank_you')  # Replace with your URL name
                else:
                    form.add_error(None, 'Flask server error.')
            except requests.exceptions.RequestException:
                form.add_error(None, 'Could not connect to Flask server.')
    else:
        form = FeedbackForm()
    return render(request, 'feedback_form.html', {'form': form})


def thank_you(request):
    return render(request, 'thank_you.html')
