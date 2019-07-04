import json
import string
import uuid
from datetime import date, datetime

from django.shortcuts import render_to_response, render
from SyllabusTrackerApp.models import Jitsuka, Membership, Kyu, RegistrationRequest
from SyllabusTrackerApp.forms import ImageForm, ProfileForm, RegisterForm, LoginForm, MembershipForm
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
from django.urls import reverse

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
        target_url = reverse('register_confirm', kwargs={'name':the_user.username, 'id':reg_id})
        msg = "<html><body>Click on this link to confirm you membership:<a href=\""+target_url+"\">"+target_url+"</a></body></html>"
        send_mail('SyllabusTracker: Confirm your registration', msg, 'dont_reply@SyllabusTracker.club', [the_user.email])
        messages.info(request, "Check your email '"+the_user.email+"' for your activation link!")
        return HttpResponseRedirect("/")

    return render(request, "SyllabusTrackerApp/register.html", {
            'register_form'		: register_form,
            'login_form'		: LoginForm(),
            'title'				: "Register"
        })


def register_confirm(request, name, id):
    if ''!=id:
        try:
            reg = RegistrationRequest.objects.get(guid=id)
            usr = reg.user

            returnObject = redirect("/profile/")
            if(usr.username != name):
                messages.error(request, "Sorry, \""+name+"\", this request seems to have come from a different user - please register again!")
                returnObject = redirect("/register/")
            else:
                day_delta = datetime.today().date() - reg.request_date    
                if day_delta.days<14:
                    usr.is_active = True
                    usr.save()
                    messages.info(request, "Welcome \""+usr.username+"\"! Please log in to fill in your membership data!")
                else:
                    messages.error(request, "Sorry, \""+usr.username+"\", you made this request more than 14 days ago, please register again!")
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
def user_update(request):
    existing_user = Jitsuka.objects.get(username=request.POST['username'])
    profile_form = ProfileForm(request.POST, instance=existing_user)
    if(profile_form.is_valid()):
        profile_form.save()
        messages.info(request, "User data successfully updated!")
    else:
        for value in profile_form.errors.items():
            messages.error(request, value)

    return redirect('/profile/')

@login_required
def membership_update(request):
    membership_form = MembershipForm(request.POST, request.FILES)
    if 'membership_id' in request.POST and request.POST['membership_id'] != '':
        membership = Membership.objects.get(id=request.POST['membership_id'])
        membership_form = MembershipForm(request.POST, request.FILES, instance=membership)

    # This alwyays needs to be forwarded
    the_user = Jitsuka.objects.get(id=request.POST['user_id'])
    if(membership_form.is_valid()):
        instance = membership_form.save()
        instance.user = the_user
        instance.save()
        messages.info(request, "Membership data successfully updated!")
    else:
        for value in membership_form.errors.items():
            messages.error(request, value)

    return redirect('/profile/')

@login_required
def profile(request, username=None):
    tisMe = True
    theUser = request.user
    membership_form = MembershipForm(initial={'user_id':theUser.id})
    found_membership = False
    can_edit = request.user.is_assistent_instructor_or_instructor()

    try:
        if (can_edit and
            None!=username) and \
            "me"!=username and \
            (None!=username and username!=request.user.username):
                theUser = Jitsuka.objects.get(username=username)
                tisMe = False
 
        membership = Membership.objects.get(user = theUser)
        membership_form = MembershipForm(instance = membership, initial={
            'membership_id':membership.id,
            'user_id':theUser.id, 
            'insurance_expiry':membership.insurance_expiry_date
            })
        membership_form.fields['instructor'].queryset = Jitsuka.objects.filter(groups__name='Instructors').exclude(membership=membership)
        membership_form.fields['insurance_expiry'].disabled = not can_edit
        found_membership = True
    except ObjectDoesNotExist:
        pass
 
    profile_form = ProfileForm(instance=theUser, initial={'username' : theUser.username})
    return render(request, "SyllabusTrackerApp/profile.html", {
        'user_controller':Jitsuka.objects,
        'tisMe':tisMe,
        'membership_form':membership_form,
        'login_form':profile_form,
        'title': ("Profile of "+theUser.username),
        'found_membership':found_membership
        })