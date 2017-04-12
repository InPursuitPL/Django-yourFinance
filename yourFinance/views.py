from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, formset_factory

from .models import Stash, Profile
from .forms import RegistrationForm, StashWithoutDateForm, StashForm, DateForm, NameForm, PeriodForm


def make_initial_list(elementName, choicesString):
    list = []
    choicesList = choicesString.split('\n')
    for i, elem in enumerate(choicesList):
        list.append({elementName:  choicesList[i]})
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
    userProfile = Profile.objects.get(user=request.user)
    stashNamesNumber = len(userProfile.stashNames.split('\n'))
    print(userProfile.stashNames)
    StashFormSet = modelformset_factory(Stash, form=StashWithoutDateForm, extra=stashNamesNumber-1)
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
                           initial=make_initial_list('name', userProfile.stashNames))
    return render(request, 'yourFinance/add_data.html',
                  {'form': form, 'formset': formset})

@login_required
def view_data(request):
    templateText = "Provide start and end date to view data in certain period of time." \
                   " Press 'submit' button without given dates to view all data."
    if request.method == 'POST':
        form = PeriodForm(request.POST)
        if form.is_valid():
            if not form.has_changed():
                stashes = Stash.objects.filter(user=request.user).order_by('date')
            else:
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
    # I've used here 'Easy Form Views Pattern' just to test it but i will
    # not change other views to it, as there are some edge cases where this
    # pattern will fail in an unexpected way. Explicit form seems also to
    # be more pythonic.
    form = StashForm(request.POST or None, instance=stash)
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
def delete_multiple_data(request):
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

@login_required
def configure_deposition_places(request):
    userProfile = Profile.objects.get(user=request.user)
    StashNameFormSet = formset_factory(NameForm, extra=1)
    if request.method == 'POST':
        formset = StashNameFormSet(request.POST)
        if formset.is_valid():
            newString = ''
            for dictionary in formset.cleaned_data:
                print(dictionary)
                if dictionary and not dictionary['name']=='':
                    newString += dictionary['name'] + '\n'
            userProfile.stashNames = newString
            userProfile.save()
            return render(request, 'yourFinance/success.html')
    formset = StashNameFormSet(initial=make_initial_list('name', userProfile.stashNames))
    return render(request, 'yourFinance/configure_deposition_places.html',
                  {'formset': formset})

