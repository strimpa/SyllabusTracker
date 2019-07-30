from .models import Membership, Notification
from .forms import LoginForm
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

    notifications = Notification.objects.filter(user=request.user)

    context = {
        'title':"Home",
        'notifications':notifications
    }
    return render(request, 'SyllabusTrackerApp/home.html', context)
