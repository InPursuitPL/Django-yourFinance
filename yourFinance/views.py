from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, formset_factory

from .models import Stash, Profile
from .forms import RegistrationForm, StashWithoutDateForm, StashForm, \
    DateForm, NameForm, PeriodForm, MonthlyCostsForm, CostGroupsForm


def make_initial_list(elementName, choicesString):
    """Helper function to make initial list in formset."""
    list = []
    choicesList = choicesString.split('\n')
    for i, elem in enumerate(choicesList):
        if choicesList[i] != '':
            list.append({elementName:  choicesList[i]})
    return list

def custom_split(choicesString):
    """
    Helper function to create list from string, based on \n but
    with no empty element at last place of the list if string
    ends with \n, as normal .split method would do.
    """
    choicesList = choicesString.split('\n')
    for element in choicesList:
        if element == '':
            choicesList.remove(element)
    return choicesList


def _give_newest_and_total_and_date(objects):
    """
    Helper function for analyzing data. Gives newest objects from
    queryset, total sum stored in their amounts and their common date.
     """
    newestObject = objects.reverse()[0]
    newestObjectsGroup = []
    totalAmount = 0
    for object in objects:
        if object.date == newestObject.date:
            newestObjectsGroup.append(object)
            totalAmount += object.amount
    return (newestObjectsGroup, totalAmount, newestObject.date)


def index(request):
    return render(request, 'yourFinance/index.html')

def sample_user_login(request):
    """Logs in sampleUser if exists"""
    username = 'sampleUser'
    password = 'justanexample'
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return render(request, 'yourFinance/index.html')
    templateText = 'There is no sample user yet!'
    return render(request, 'yourFinance/failure.html', {'templateText': templateText})


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
def view_profile(request):
    """Displays view user profile page with links to configuration options."""
    userProfile = Profile.objects.get(user=request.user)
    stashNamesList = custom_split(userProfile.stashNames)
    costNamesList = custom_split(userProfile.costNames)
    return render(request,
                  'registration/view_profile.html',
                  {'stashNamesList': stashNamesList,
                   'costNamesList': costNamesList})

@login_required
def add_data(request):
    """Creates new Stash objects based on user StashNames field."""
    userProfile = Profile.objects.get(user=request.user)
    stashNamesNumber = len(userProfile.stashNames.split('\n'))
    StashFormSet = modelformset_factory(Stash,
                                        form=StashWithoutDateForm,
                                        extra=stashNamesNumber-1)
    if request.method == 'POST':
        form = DateForm(request.POST)
        formset = StashFormSet(request.POST)
        if form.is_valid() and formset.is_valid()and form.has_changed():
            stashList = formset.save(commit=False)
            templateText = '{} entries were added.'.format(len(stashList))
            for stash in stashList:
                stash.user = request.user
                stash.date = form.cleaned_data['date']
                stash.save()
            return render(request,
                          'yourFinance/success.html',
                          {'templateText': templateText,})
        else:
            return render(request, 'yourFinance/add_data.html',
                          {'form': form, 'formset': formset})
    form = DateForm()
    formset = StashFormSet(queryset=Stash.objects.none(),
                           initial=make_initial_list('name',
                                                     userProfile.stashNames))
    return render(request, 'yourFinance/add_data.html',
                  {'form': form, 'formset': formset})

def stashes_with_total_amounts(stashesList):
    """
    Helper function to format output for view_data with
    stashes groups and total amounts for each group.
    """
    # Creates object because template will use its stashes_date argument
    # for group_delete view link and its __str__ method to show information.
    class Container:
        def __init__(self, stashes_date, total_amount):
            self.stashes_date = stashes_date
            self.total_amount = total_amount
        def __str__(self):
            return 'Total amount for {}: {}'.format(self.stashes_date,
                                                    self.total_amount)
    nested_list = []
    stashes_group_list = []
    total_amount = 0
    # Output is in the format [[
    # [stash1, stash2, ...],
    # [Container_object_with_date_and_amount_for_preceding_group,]],
    # [[stash4, stash5, ...],
    # [Container_object,]],  ... ]
    for stash in stashesList:
        stashes_group_list.append(stash)
        total_amount += stash.amount
        stashes_date = stash.date
        if stash == stashesList[len(stashesList) - 1] or \
                        stashesList[stashesList.index(stash) + 1].date != stash.date:
            stashes_and_total_list = []
            stashes_and_total_list.append(stashes_group_list)
            stashes_group_list = []
            group_element = Container(stashes_date, total_amount)
            stashes_and_total_list.append([group_element, ])
            nested_list.append(stashes_and_total_list)
            total_amount = 0
    return nested_list

@login_required
def view_data(request):
    """
    Displays all Stash data or data from date range
    together with total amount for certain date.
    """
    templateText = "Provide start and end date to view data in " \
                   "certain period of time. Press 'submit' button " \
                   "without given dates to view all data."
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
            #Queryset into list.
            stashesList = []
            for element in stashes:
                stashesList.append(element)
            # usage of helper function to create output for the template.
            stashes_groups_and_totals = stashes_with_total_amounts(stashesList)
            return render(request,
                          'yourFinance/view_data.html',
                          {'stashes_groups_and_totals': stashes_groups_and_totals})
        else:
            return render(request, 'yourFinance/choose_time.html',
                          {'form': form,
                           'templateText': templateText,
                           'buttonName': 'Show'})
    form = PeriodForm()
    return render(request, 'yourFinance/choose_time.html',
                  {'form': form,
                   'templateText': templateText,
                   'buttonName': 'Show'})

@login_required
def data_edit(request, pk):
    """Edit single Stash entry."""
    message = 'Here you can edit chosen data.'
    stash = get_object_or_404(Stash, pk=pk)
    # Forbids other users to see and edit someones stash
    # by manually providing certain url.
    if stash.user != request.user:
        message = 'Access denied!'
        return render(request, 'yourFinance/failure.html',
                      {'templateText': message})
    # I've used here 'Easy Form Views Pattern' just to test it but i will
    # not change other views to it, as there are some edge cases where this
    # pattern will fail in an unexpected way. Explicit form seems also to
    # be more pythonic.
    form = StashForm(request.POST or None, instance=stash)
    if form.is_valid():
        form.save()
        return render(request, 'yourFinance/success.html')
    return render(request,
                  'yourFinance/data_form.html',
                  {'form': form, 'message': message})

@login_required
def data_delete(request, pk):
    """Delete single Stash entry."""
    stash = get_object_or_404(Stash, pk=pk)
    # Forbids other users to see and delete someones stash
    # by manually providing certain url.
    if stash.user != request.user:
        message = 'Access denied!'
        return render(request, 'yourFinance/failure.html',
                      {'templateText': message})
    if request.method == 'POST':
        stash.delete()
        return render(request, 'yourFinance/success.html')
    return render(request, 'yourFinance/confirm_delete.html')

@login_required
def group_delete(request, date):
    """Deletes stashes group for given date."""
    stashes = Stash.objects.filter(user=request.user,
                date=date)
    if request.method == 'POST':
        for stash in stashes:
            stash.delete()
        return render(request, 'yourFinance/success.html')
    return render(request, 'yourFinance/confirm_delete.html',
                  {'stashes': stashes})

@login_required
def delete_multiple_data(request):
    """Delete multiple Stash objects according to date range."""
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
            return render(request,
                          'yourFinance/success.html',
                          {'templateText': templateText,})
        else:
            return render(request, 'yourFinance/choose_time.html',
                          {'form': form,
                           'templateText': templateText,
                           'buttonName': 'Delete'})
    form = PeriodForm()
    return render(request, 'yourFinance/choose_time.html',
                  {'form': form,
                   'templateText': templateText,
                   'buttonName': 'Delete'})

@login_required
def analyze_data(request):
    """Possibility to decide if analyze last data entries or choose date."""
    message = "Provide date for which you would like your data to be " \
              "analyzed. Press 'submit' button without given date to " \
              "analyze newest record. If you'll choose date for which " \
              "there are no data, records closest to the date (but not" \
              " after it) will be taken."
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            if form.cleaned_data['date'] == None:
                date = '9999-12-31'
            return redirect('analyze record', date=date)
    form = DateForm()
    return render(request,
                  'yourFinance/data_form.html',
                  {'form': form, 'message': message})

@login_required
def analyze_record(request, date):
    """Analyzes data requested in analyze_data view."""

    userProfile = Profile.objects.get(user=request.user)
    allStashes = Stash.objects.filter(user=request.user).order_by('date')
    # If there are no data, returns without analyzing.
    if not len(allStashes) > 0:
        return render(request, 'yourFinance/failure.html', {'templateText': 'No data to analyze!'})

    # Collecting newest/required data entries.
    chosenStashes = Stash.objects.filter(user=request.user, date__lte=date).order_by('date')
    (newestStashesGroup,
    totalAmount,
    newestStashesDate) = _give_newest_and_total_and_date(chosenStashes)

    # Collecting data entries previous to newest/required ones.
    previousStashes = chosenStashes.exclude(date=newestStashesDate).order_by('date')
    # If there are any data from before newest/required ones, it will view it.
    if len(previousStashes) > 0:
        arePrevious = True
        messagePrevious = 'Data from previous record: '
        (previousStashesGroup,
         previousTotalAmount,
         previousStashesDate) = _give_newest_and_total_and_date(previousStashes)
        previousTotalStatement = 'Total sum: {}'.format(previousTotalAmount)
        gain = totalAmount - previousTotalAmount
        if gain >= 0:
            messageGain = 'You have gained {}'.format(gain)
        else:
            messageGain = 'You have lost {}'.format(abs(gain))
    # If there are no previous data, only information about it will be visible.
    else:
        arePrevious = False
        messagePrevious = 'No previous data in database.'

    # Part to analyze for how long current sum will be enough.
    monthlyCostsList = [(userProfile.basicLevel, 'basic level'),
                        (userProfile.mediumLevel, 'medium level'),
                        (userProfile.standardLevel, 'standard level')]
    monthlyCostsStrings = []
    for amount in monthlyCostsList:
        monthlyCostsStrings.append('{} months'
                                   ' based on {} amount of {}.'.format(
            round(totalAmount / amount[0], 1),
            amount[0],
            amount[1]))

    # Part to ask in formset and analyze expenses in cost groups.
    CostGroupsFormSet = formset_factory(CostGroupsForm, extra=0)
    afterCostsMessage = ''
    if request.method == 'POST':
        cost_groups_formset = CostGroupsFormSet(request.POST)
        if cost_groups_formset.is_valid():
            totalCosts = 0
            totalAmountAfterExpenses = float(totalAmount)
            for dictionary in cost_groups_formset.cleaned_data:
                totalCosts += dictionary['amount']
                totalAmountAfterExpenses -= dictionary['amount']
            afterCostsMessage = 'Total current costs: {}.' \
                                ' Amount after expenses: {}' \
                .format(round(totalCosts, 2), round(totalAmountAfterExpenses, 2))
    else:
        cost_groups_formset = CostGroupsFormSet(
            initial=make_initial_list('name', userProfile.costNames)
        )
        afterCostsMessage = ''
    templateDict = {'newestStashesGroup': newestStashesGroup,
                    'totalAmount': totalAmount,
                    'messagePrevious': messagePrevious,
                    'monthlyCostsStrings': monthlyCostsStrings,
                    'formset': cost_groups_formset,
                    'afterCostsMessage': afterCostsMessage
                    }
    # Added only if there were previous data before newest/required ones.
    if arePrevious:
        templateDict['newestPreviousGroup'] = previousStashesGroup
        templateDict['previousTotalStatement'] = previousTotalStatement
        templateDict['messageGain'] = messageGain

    return render(request, 'yourFinance/analyze.html', templateDict)

@login_required
def configure_deposition_places(request):
    """Enables configuring user stashNames field, stored in Profile model."""
    userProfile = Profile.objects.get(user=request.user)
    StashNameFormSet = formset_factory(NameForm, extra=1)
    if request.method == 'POST':
        formset = StashNameFormSet(request.POST)
        if formset.is_valid():
            newString = ''
            for dictionary in formset.cleaned_data:
                if dictionary and not dictionary['name']=='':
                    newString += dictionary['name'] + '\n'
            userProfile.stashNames = newString
            userProfile.save()
            return render(request, 'yourFinance/success.html')
    formset = StashNameFormSet(
        initial=make_initial_list('name', userProfile.stashNames)
    )
    return render(request, 'yourFinance/configure_names.html',
                  {'formset': formset})

@login_required
def configure_cost_groups(request):
    """Enables configuring user costNames field, stored in Profile model."""
    userProfile = Profile.objects.get(user=request.user)
    CostNameFormSet = formset_factory(NameForm, extra=1)
    if request.method == 'POST':
        formset = CostNameFormSet(request.POST)
        if formset.is_valid():
            newString = ''
            for dictionary in formset.cleaned_data:
                if dictionary and not dictionary['name']=='':
                    newString += dictionary['name'] + '\n'
            userProfile.costNames = newString
            userProfile.save()
            return render(request, 'yourFinance/success.html')
    formset = CostNameFormSet(
        initial=make_initial_list('name', userProfile.costNames)
    )
    return render(request, 'yourFinance/configure_names.html',
                  {'formset': formset})

@login_required
def configure_monthly_costs(request):
    """
    Enables configuring user monthly cost fields,
    stored in Profile model.
    """
    userProfile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = MonthlyCostsForm(request.POST)
        if form.is_valid():
            userProfile.basicLevel = form.cleaned_data['basicLevel']
            userProfile.mediumLevel = form.cleaned_data['mediumLevel']
            userProfile.standardLevel = form.cleaned_data['standardLevel']
            userProfile.save()
            return render(request, 'yourFinance/success.html')
    form = MonthlyCostsForm(instance=userProfile)
    return render(request,
                  'yourFinance/configure_monthly_costs.html',
                  {'form': form})