from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from django.db import IntegrityError
from django.contrib.auth import authenticate, login

CATEGORY_CHOICES = ['Food', 'Beauty', 'Politics', 'Travel', 'Lifestyle']

from AuthApp.models import Profile  # make sure this import is at the top

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        selected_categories = request.POST.getlist('categories')
        role = request.POST.get('role')  # collect role

        if password != confirm_password:
            message = "Passwords do not match!!"
            return render(request, 'signup.html', {'categories': CATEGORY_CHOICES},{'message': message})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!!")
            return redirect('AuthApp:login')

        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email already exists... Please Login!!")
            return redirect('AuthApp:login')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)

            profile = Profile.objects.create(
                user=user,
                categories=', '.join(selected_categories)
            )

            request.session['interests'] = profile.categories
            request.session['role'] = role

            messages.success(request, "User registered successfully!")
            return redirect('AuthApp:login')

        except IntegrityError:
            messages.error(request, "Something went wrong. Please try again.")
            return render(request, 'signup.html', {'categories': CATEGORY_CHOICES})

    return render(request, 'signup.html', {'categories': CATEGORY_CHOICES})




def login_view(request):
    message = ""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            message = "No account found with this email."
            return render(request, 'login.html', {'message': message})

        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            if role == "admin" and user.is_superuser:
                login(request, user)
                return redirect("dashboard")
            elif role == "user" and not user.is_superuser:
                login(request, user)
                return redirect("dashboard")
            else:
                message = f"Login type '{role}' doesn't match your account permissions."
        else:
            message = "Incorrect password."

    return render(request, 'login.html', {'message': message})


def dashboard_view(request):
    return render(request, 'index.html')

