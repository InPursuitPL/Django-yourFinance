from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory

from .models import Stash
from .forms import RegistrationForm, StashForm


def make_choices_list(elementName, choicesTuple):
	list = []
	for i, elem in enumerate(choicesTuple):
		list.append({elementName:  choicesTuple[i][0]})
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
def add_data(request):
    StashFormSet = modelformset_factory(Stash, form=StashForm, extra=4)
    if request.method == 'POST':
        formset = StashFormSet(request.POST)
        if formset.is_valid():
            stash = formset.save(commit=False)
            stash.user = request.user
            stash.save()
            return render(request, 'yourFinance/success.html')

        else:
            return render(request, 'yourFinance/add_data.html', {'formset': formset})
    formset = StashFormSet(queryset=Stash.objects.none(),
                           initial=make_choices_list('name', Stash.NAME_CHOICES))
    return render(request, 'yourFinance/add_data.html', {'formset': formset})

@login_required
def view_all_data(request):
    stashes = Stash.objects.filter(user=request.user).order_by('date')
    return render(request, 'yourFinance/view_data.html', {'stashes': stashes})
