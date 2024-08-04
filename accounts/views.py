from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
# from netconfapp.models import Log
# from .forms import NetworkAdminSignupForm

def network_admin_signup(request):
    '''
    :param request: HTTP request object.
    :return: Redirect to home page or rendered Sign Up page.
    '''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Log.objects.create(user=user, action='Signed up and logged in', success=True)
            return redirect('home')  # Redirect to home page
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def network_admin_login(request):
    '''
    :param request: HTTP request object.
    :return: Redirect to home page or rendered Sign In page.
    '''
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                
                    login(request, user)
                    # Log.objects.create(user=user, action='Logged in', success=True)
                    return redirect('home')  # Redirect to home page
                
            else:
                pass
                #  Log.objects.create(action=f'Failed login attempt for user: {username}', success=False)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_admin(request):
    '''
    :param request: HTTP request object.
    :return: Redirect to Sign In page.
    '''
    user = request.user
    logout(request)
    # Log.objects.create(user=user, action='Logged out', success=True)
    return redirect('home')

