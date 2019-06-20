from .models import Exercise, Session, Rating, Membership, Kyu, ExerciseGroup
from .forms import LoginForm, ExerciseForm, ExerciseEditForm, UploadFileForm, KyuForm, ExerciseGroupForm
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required 
from .view_utils import *

def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/user_home/') # Redirect after POST
    next = '/user_home/'
    if 'next' in request.GET:
        next = request.GET['next']
    return render(request, 'SyllabusTrackerApp/index.html', 
        {
            'title':"Start",
            'login_form':LoginForm(),
            'target_url':next
        })

@login_required
def home(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    latest_session_list = Session.objects.all()[:5]
    context = {
        'title':"Home",
        'latest_session_list': latest_session_list,
        'login_form':LoginForm()
    }
    return render(request, 'SyllabusTrackerApp/home.html', context)

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
