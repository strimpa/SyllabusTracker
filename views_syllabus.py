from .models import Exercise, Session, Rating, Membership, Kyu, ExerciseGroup
from .forms import LoginForm, ExerciseForm, ExerciseEditForm, UploadFileForm, KyuForm, ExerciseGroupForm
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .data_processing import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .view_utils import *

@login_required
@permission_required('SyllabusTrackerApp.change_exercise')
def exercise_editing(request, successful_add=False):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    all_groups = ExerciseGroup.objects.all()
    ExerciseGroupFormSet = modelformset_factory(ExerciseGroup, form=ExerciseGroupForm, can_delete=True, exclude=(), extra=0)
    ExerciseFormSet = modelformset_factory(Exercise, form=ExerciseEditForm, can_delete=True, exclude=(), extra=0)

    add_ex_form = ExerciseForm()
    exercise_csv_form = UploadFileForm()
    ex_edit_form = ExerciseFormSet(initial=Exercise.objects.all().values())
    context = {
        'title':"Exercise Editing",
        'exercise_formset':ex_edit_form,
        'all_groups':all_groups,
        'add_ex_form':add_ex_form,
        'successful_add':successful_add,
        'exercise_csv_form':exercise_csv_form,
        'exercise_group_formset':ExerciseGroupFormSet(initial=all_groups.values()),
        'add_ex_group_form':ExerciseGroupForm()
    }
    return render(request, 'SyllabusTrackerApp/exercise_editing.html', context)

@login_required
def sessions(request):
    check_membership(request.user)

    return HttpResponse("Showing the sessions table")

@login_required
@permission_required('SyllabusTrackerApp.add_session', raise_exception=True)
def edit_session(request, id=None):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    session_form = SessionForm()
    if kyu_form.is_valid():
        kyu = Kyu(grade=kyu_form.cleaned_data['grade'], colour=kyu_form.cleaned_data['colour'])
        kyu.save()
    
    KyuFormSet = formset_factory(KyuForm)
    context = {
        'existing_kyu_form':KyuFormSet(initial=Kyu.objects.all().values()),
        'add_kyu_form':KyuForm()
    }
    return render(request, 'SyllabusTrackerApp/add_kyus.html', context)
