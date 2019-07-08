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
from django.template.loader import render_to_string
from django.contrib.auth.models import Group

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
        target_url = request.META['HTTP_HOST']
        target_url += reverse('register_confirm', kwargs={'name':the_user.username, 'id':reg_id})

        template_values = {
            'name':the_user.first_name,
            'target_url':target_url,
            'email':the_user.email
        }        
        msg_plain = render_to_string('registration_email.txt', template_values)
        msg_html = render_to_string('registration_email.html', template_values)
        send_mail(
            '[SyllabusTracker] Registration confirmation',
            msg_plain,
            None,
            [template_values['email']],
            html_message=msg_html,
        )

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
    forward_username = ""
    try:
        existing_user = Jitsuka.objects.get(username=request.POST['username'])
        if existing_user!=request.user:
            forward_username = existing_user.username
        profile_form = ProfileForm(request.POST, instance=existing_user)
        if(profile_form.is_valid()):
            profile_form.save()
            messages.info(request, "User data successfully updated!")
        else:
            for value in profile_form.errors.items():
                messages.error(request, value)
    except:
        messages.error(request, "Error while updating user")
    return redirect('/profile/'+forward_username)

@login_required
def membership_update(request):
    forward_username = ""
    membership_form = MembershipForm(request.POST, request.FILES)
    if 'membership_id' in request.POST and request.POST['membership_id'] != '':
        membership = Membership.objects.get(id=request.POST['membership_id'])
        membership_form = MembershipForm(request.POST, request.FILES, instance=membership)

    try:
        # This alwyays needs to be forwarded
        the_user = Jitsuka.objects.get(id=request.POST['user_id'])
        if the_user!=request.user:
            forward_username = the_user.username
        if(membership_form.is_valid()):
            instance = membership_form.save()
            instance.user = the_user
            instance.save()

            try:
                instructor_group = Group.objects.get(name='Instructors')
                if membership_form.cleaned_data['is_instructor']:
                    instructor_group.user_set.add(the_user)
                else:
                    instructor_group.user_set.remove(the_user)
            except:
                pass

            try:
                assistent_instructor_group = Group.objects.get(name='Assistent Instructors') 
                if membership_form.cleaned_data['is_assistent_instructor']:
                    assistent_instructor_group.user_set.add(the_user)
                else:
                    assistent_instructor_group.user_set.remove(the_user)
            except:
                pass

            messages.info(request, "Membership data successfully updated!")
        else:
            for value in membership_form.errors.items():
                messages.error(request, value)
    except:
        messages.error(request, "Error while updating memberhsip")
    return redirect('/profile/'+forward_username)

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
    except:
        messages.error(request, "User with name '"+username+"' does not exist!")

    is_instructor = False
    is_assistent_instructor = False
    try:
        is_instructor = Group.objects.get(name='Instructors').user_set.filter(id = theUser.id).exists()
        is_assistent_instructor = Group.objects.get(name='Assistent Instructors').user_set.filter(id = theUser.id).exists()
    except:
        pass

    try:
        membership = Membership.objects.get(user = theUser)
        found_membership = True
        membership_form = MembershipForm(instance = membership, initial={
            'membership_id':membership.id,
            'user_id':theUser.id, 
            'insurance_expiry':membership.insurance_expiry_date,
            'is_instructor':is_instructor,
            'is_assistent_instructor':is_assistent_instructor
            })
    except:
        pass

    try:
        membership_form.fields['instructor'].queryset = Jitsuka.objects.filter(groups__name='Instructors').exclude(membership=membership)
    except ObjectDoesNotExist:
        pass
    membership_form.fields['insurance_expiry_date'].disabled = not can_edit
    membership_form.fields['is_instructor'].disabled = not can_edit
    membership_form.fields['is_assistent_instructor'].disabled = not can_edit
 
    profile_form = ProfileForm(instance=theUser, initial={'username' : theUser.username})
    return render(request, "SyllabusTrackerApp/profile.html", {
        'user_controller':Jitsuka.objects,
        'tisMe':tisMe,
        'membership_form':membership_form,
        'login_form':profile_form,
        'title': ("Profile of "+theUser.username),
        'found_membership':found_membership
        })