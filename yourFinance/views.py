from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory

from .models import Stash
from .forms import RegistrationForm, StashForm, DateForm


def make_initial_list(elementName, choicesTuple, secondElementName, date):
	list = []
	for i, elem in enumerate(choicesTuple):
		list.append({elementName:  choicesTuple[i][0],
                     secondElementName: date})
	return list


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

@login_required
def set_date(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            return redirect('add data', date=form.cleaned_data['date'])
        else:
            return render(request, 'yourFinance/set_date.html', {'form': form})
    form = DateForm()
    return render(request, 'yourFinance/set_date.html', {'form': form})

@login_required
def add_data(request, date):
    StashFormSet = modelformset_factory(Stash, form=StashForm, extra=4)
    if request.method == 'POST':
        formset = StashFormSet(request.POST)
        if formset.is_valid():
            stashList = formset.save(commit=False)
            for stash in stashList:
                stash.user = request.user
                stash.save()
            return render(request, 'yourFinance/success.html')
        else:
            return render(request, 'yourFinance/add_data.html', {'formset': formset})
    formset = StashFormSet(queryset=Stash.objects.none(),
                           initial=make_initial_list('name', Stash.NAME_CHOICES,
                                                     'date', date))
    return render(request, 'yourFinance/add_data.html', {'formset': formset})

@login_required
def view_all_data(request):
    stashes = Stash.objects.filter(user=request.user).order_by('date')
    return render(request, 'yourFinance/view_data.html', {'stashes': stashes})
