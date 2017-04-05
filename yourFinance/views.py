from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory

from .models import Stash
from .forms import RegistrationForm, StashForm, StashFullForm, DateForm, PeriodForm


def make_initial_list(elementName, choicesTuple):
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
        form = DateForm(request.POST)
        formset = StashFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            stashList = formset.save(commit=False)
            for stash in stashList:
                stash.user = request.user
                stash.date = form.cleaned_data['date']
                stash.save()
            return render(request, 'yourFinance/success.html')
        else:
            return render(request, 'yourFinance/add_data.html',
                          {'form': form, 'formset': formset})
    form = DateForm()
    formset = StashFormSet(queryset=Stash.objects.none(),
                           initial=make_initial_list('name', Stash.NAME_CHOICES))
    return render(request, 'yourFinance/add_data.html',
                  {'form': form, 'formset': formset})

@login_required
def view_all_data(request):
    stashes = Stash.objects.filter(user=request.user).order_by('date')
    return render(request, 'yourFinance/view_data.html', {'stashes': stashes})

@login_required
def view_certain_data(request):
    templateText = 'Provie start and end date to view data in certain period of time.'
    if request.method == 'POST':
        form = PeriodForm(request.POST)
        if form.is_valid():
            stashes = Stash.objects.filter(
                user=request.user,
                date__range=(form.cleaned_data['startDate'],
                             form.cleaned_data['endDate'])
            ).order_by('date')
            return render(request, 'yourFinance/view_data.html', {'stashes': stashes})
        else:
            return render(request, 'yourFinance/choose_time.html',
                          {'form': form, 'templateText': templateText, 'buttonName': 'Show'})
    form = PeriodForm()
    return render(request, 'yourFinance/choose_time.html',
                  {'form': form, 'templateText': templateText, 'buttonName': 'Show'})

@login_required
def data_edit(request, pk):
    stash = get_object_or_404(Stash, pk=pk)
    form = StashFullForm(request.POST or None, instance=stash)
    if form.is_valid():
        form.save()
        return render(request, 'yourFinance/success.html')
    return render(request, 'yourFinance/data_form.html', {'form': form})

@login_required
def data_delete(request, pk):
    stash = get_object_or_404(Stash, pk=pk)
    if request.method == 'POST':
        stash.delete()
        return render(request, 'yourFinance/success.html')
    return render(request, 'yourFinance/confirm_delete.html')

@login_required
def delete_data(request):
    templateText = 'Warning! Data from certain period of time will be deleted!'
    if request.method == 'POST':
        form = PeriodForm(request.POST)
        if form.is_valid():
            stashes = Stash.objects.filter(
                user=request.user,
                date__range=(form.cleaned_data['startDate'],
                             form.cleaned_data['endDate'])
            ).order_by('date')
            stashesAmount = len(stashes)
            for stash in stashes:
                stash.delete()
            templateText = '{} entries were deleted.'.format(stashesAmount)
            return render(request, 'yourFinance/success.html', {'templateText': templateText,})
        else:
            return render(request, 'yourFinance/choose_time.html',
                          {'form': form, 'templateText': templateText, 'buttonName': 'Delete'})
    form = PeriodForm()
    return render(request, 'yourFinance/choose_time.html',
                  {'form': form, 'templateText': templateText, 'buttonName': 'Delete'})