import json
import string
import uuid
from datetime import date, datetime

from django.shortcuts import render_to_response, render
from SyllabusTrackerApp.models import Jitsuka, Membership, Kyu, RegistrationRequest
from SyllabusTrackerApp.forms import AccountForm, ImageForm, ProfileForm, RegisterForm, LoginForm, MembershipForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import SetPasswordForm, UserChangeForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .view_utils import *

def login_request(request):

    if request.method == "POST":
        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            try:
                user = Jitsuka.objects.get(username=username)
            except ObjectDoesNotExist:
                return render(request, "SyllabusTrackerApp/deadend.html", {
                                'login_form':LoginForm(),
                                'warning_text':"No user with that name."
                                })

            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user is None:
                # no user with that name
                warning_text = "Wrong password."
                return render(request, "SyllabusTrackerApp/deadend.html", {
                                'login_form':LoginForm(),
                                'warning_text':warning_text
                                })

            #user isn't activated yet
            if not authenticated_user.is_active:
                #user isn't activated yet
                return render(request, "SyllabusTrackerApp/deadend.html", {
                                'login_form':LoginForm(),
                                'warning_text':"User hasn't been activated yet. Please check your email."
                                })

            # SUCCESS!
            login(request, authenticated_user)
            target_url = '/user_home/'
            if 'target_url' in request.POST:
                target_url = request.POST['target_url']
            return HttpResponseRedirect(target_url) # Redirect after POST

    return render(request, "/", {
        'login_form':LoginForm(),
        })

@login_required
def forgot_password(request):
    return render(request, "SyllabusTrackerApp/login.html", {
        'login_form':LoginForm(),
        })

@login_required
def logout_request(request):
    logout(request)
    return HttpResponseRedirect("/")

    
def register(request):
    register_form = RegisterForm()

    if request.method == "POST":
        register_form = RegisterForm(request.POST, request.FILES)
    if register_form.is_valid():
        the_user = Jitsuka.objects.create_user(
            register_form.cleaned_data['username'], 
            register_form.cleaned_data['email'])
        register_form = RegisterForm(request.POST, request.FILES, instance=the_user)
        register_form.save()

        reg_id = uuid.uuid4()
        reg = RegistrationRequest(user=the_user, guid=reg_id)
        reg.save()

        from django.core.mail import send_mail
        send_mail('Please confirm your registration', "<a href=\"/register_confirm/?name=the_user.username&id="+str(reg_id)+"\">Click</a>", 'dont_reply@SyllabusTracker.club', [the_user.email])
        messages.info(request, "Check your email '"+the_user.email+"' for your activation link!")
        return HttpResponseRedirect("/")

    return render(request, "SyllabusTrackerApp/register.html", {
            'register_form'		: register_form,
            'login_form'		: LoginForm(),
            'title'				: "Register"
        })


def register_confirm(request):
    if request.method == "GET":
        regId = request.GET['id']
        if ''!=regId:
            try:
                reg = RegistrationRequest.objects.get(guid=regId)
                usr = reg.user
                day_delta = datetime.today().date() - reg.request_date    

                returnObject = redirect("/profile/")
                if day_delta.days<14:
                    usr.is_active = True
                    usr.save()
                    messages.info(request, "Welcome\""+usr.username+"\"! Please log in to fill in your membership data!")
                else:
                    messages.Error(request, "Sorry\""+usr.username+"\", you made this request more than 14 days ago, please register again!")
                    returnObject = redirect("/register/")

                reg.delete()
                return returnObject
            except ObjectDoesNotExist:
                pass

    confirmation_text = "registration failed"
    return render(request, "SyllabusTrackerApp/register.html", {
        'confirmation':False,
        'confirmation_text':confirmation_text,
        'register_form': RegisterForm(),
        'login_form':LoginForm(),
        'title':"Register again, please!"
        })
        

@login_required
def profile(request, username=None):
    tisMe = True
    theUser = request.user
    membership_form = MembershipForm()
    found_membership = False

    try:
        if (None!=username) and \
            "me"!=username and \
            (None!=username and username!=request.user.username):
                theUser = Jitsuka.objects.get(username=username)
                tisMe = False

        if tisMe:
            membership = Membership.objects.get(user = request.user)
            membership_form = MembershipForm(instance = membership)
            found_membership = True
    except ObjectDoesNotExist:
        pass

    if request.method == 'GET':
        if 'username' in request.GET:
            user_form = ProfileForm(request.GET, instance=request.user)
            if user_form.is_valid():
                username = user_form.data['username']
                first_name = user_form.data['first_name']
                last_name = user_form.data['last_name']
                theUser.username = username
                theUser.first_name = first_name
                theUser.last_name = last_name
                theUser.save()
            else:
                return HttpResponse("errors:"+user_form.errors.as_text())
        elif 'memberID' in request.GET:
            membership_form = MembershipForm(request.GET)
            if membership_form.is_valid():
                memberID = membership_form.cleaned_data['memberID']
                kyu = membership_form.cleaned_data['kyu']
                instructor = membership_form.cleaned_data['instructor']

                m = Membership()
                try:
                    m = Membership.objects.get(user=theUser)
                except:
                    pass
                m.user = theUser
                m.memberID = memberID
                m.kyu = kyu
                if instructor!='':
                    m.instructor = instructor
                m.save()
                m = Membership.objects.get(user=theUser)
                membership_form = MembershipForm(instance = m)
            else:
                return HttpResponse("errors:"+membership_form.errors.as_text())

    return render(request, "SyllabusTrackerApp/profile.html", {
        'user_controller':Jitsuka.objects,
        'tisMe':tisMe,
        'membership_form':membership_form,
        'login_form':ProfileForm(instance=theUser),
        'title': ("Profile of "+theUser.username),
        'found_membership':found_membership
        })