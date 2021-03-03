from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

# Create your views here.


def register(request):
    if request.user.is_authenticated:
        username = request.user
        messages.info(request, f'Welcome {username} ! Have a great time doing recon.')
        return redirect('dashboard')
    else:
        form = UserRegisterForm()
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, f'Successfully created an account for {username}.')
                return redirect('login')

        context = {'form': form}
        return render(request, 'users/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        username = request.user
        messages.info(request, f'Welcome {username} ! Have a great time doing recon.')
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('register')
            else:
                messages.warning(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'users/login.html', context)


def logoutUser(request):
    logout(request)
    username = request.user
    messages.info(request, f'Thank you for visiting us. Have a good day.')
    return redirect('login')


# @login_required
# def profile(request):
#     return render(request, 'users/profile.html')
