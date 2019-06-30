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
