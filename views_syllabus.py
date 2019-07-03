from datetime import date, datetime
from .models import Exercise, Session, Rating, Membership, Kyu, ExerciseGroup, Jitsuka
from .forms import LoginForm, ExerciseForm, ExerciseEditForm, UploadFileForm, KyuForm, ExerciseGroupForm, SessionForm, SessionFormReadOnly
from django.core.paginator import Paginator
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

    exercise_page = 1
    if request.method=="GET" and 'exercise_page' in request.GET:
        exercise_page = request.GET['exercise_page']
    exercise_paginator = Paginator(Exercise.objects.all(), 10)
    page = exercise_paginator.page(exercise_page)
    print(str(page.object_list))
    ex_edit_form = ExerciseFormSet(queryset=page.object_list)

    exerciseGroup_paginator = Paginator(all_groups, 10)
    exercise_group_page = 1
    if request.method=="GET" and 'exercise_group_page' in request.GET:
        exercise_group_page = request.GET['exercise_group_page']
    page = exerciseGroup_paginator.page(exercise_group_page)
    print(str(page.object_list))
    exGroup_edit_form = ExerciseGroupFormSet(queryset=page.object_list)

    context = {
        'title':"Exercise Editing",
        'ex_edit_form':ex_edit_form,
        'add_ex_form':add_ex_form,
        'successful_add':successful_add,
        'exercise_csv_form':exercise_csv_form,
        'exGroup_edit_form':exGroup_edit_form,
        'add_ex_group_form':ExerciseGroupForm(),
        'exercise_page':exercise_page,
        'exercise_group_page':exercise_group_page
    }
    return render(request, 'SyllabusTrackerApp/exercise_editing.html', context)

@login_required
def sessions(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    context = {
        'title':"Sessions",
        "sessions":Session.objects.all(),
    }
    return render(request, 'SyllabusTrackerApp/sessions.html', context)

@login_required
def view_session(request, id=None):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    session_instance = None
    try:
        session_instance = Session.objects.get(id=id)
    except:
        messages.error(request, "Session object not found!")
        return redirect('/sessions/')

    context = {
        'title':"View Session",
        'attendants':session_instance.attendants.all(),
        'exercises':session_instance.exercises.all(),
        'date':session_instance.date,
        'instructor':session_instance.instructor,
        'session_id':session_instance.id
    }
    return render(request, 'SyllabusTrackerApp/view_session.html', context)

@login_required
@permission_required('SyllabusTrackerApp.change_session')
def edit_session(request, id=None):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    session_form = SessionForm(initial={'date':datetime.now()})
    if id!=None:
        try:
            session_instance = Session.objects.get(id=id)
            session_form = SessionForm(instance=session_instance)
        except:
            messages.info(request, "Session object not found, creating a new Session!")

    session_form.fields['instructor'].queryset = Jitsuka.objects.filter(groups__name='Instructors')

    context = {
        'title':"Edit Session",
        'session_id':id,
        'session_form':session_form,
    }
    return render(request, 'SyllabusTrackerApp/edit_sessions.html', context)
