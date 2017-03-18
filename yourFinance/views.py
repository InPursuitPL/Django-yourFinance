from django.shortcuts import render
from django.contrib.auth.models import User

from .forms import RegistrationForm


def index(request):
    return render(request, 'yourFinance/index.html')

def register_page(request):
    """Page for new user registration."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'])
            return render(request, 'registration/register_success.html',
                          {'user': form.cleaned_data['username']})
        else:
            return render(request, 'registration/register.html', {'form': form})
    form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
