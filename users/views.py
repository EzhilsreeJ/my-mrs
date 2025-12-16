from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def login_user(request):
    if request.user.is_authenticated:
        return redirect('recommendations:movie_list')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('recommendations:movie_list')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('users:login')

@login_required
def profile(request):
    # For now, the profile view is minimal. It could be expanded to show user ratings etc.
    return render(request, 'users/profile.html')