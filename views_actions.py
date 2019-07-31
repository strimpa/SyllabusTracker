from .models import Exercise, Session, Rating, Membership, Kyu, ExerciseGroup, AppSettings
from .forms import LoginForm, ExerciseForm, ExerciseEditForm, UploadFileForm, KyuForm, ExerciseGroupForm, SessionForm, SettingsForm
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .data_processing import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .view_utils import *
from django.core.mail import send_mail
from django.template.loader import render_to_string

@login_required
def back_to_editing(request, notification, current_page_string="", isError=False):
    if isError:
        messages.error(request, notification)
    else:
        messages.info(request, notification)
    return redirect('/exercise_editing/'+current_page_string)

@login_required
def do_rate(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    anchor = ""
    #processing incoming rating
    if request.method == "POST":
        data = request.POST
        group_id = data['exercise_group_id']
        if 'next' in data:
            anchor = "#"+data['next']

        for field in data:
            if 'comment_' in field:
                ex_id = field.split('_')[1]
                ex_comment = data[field]
                ex_name = data["exercise_name_"+str(ex_id)]
                ex_proficiency = data["proficiency_"+str(ex_id)]
                exercise = Exercise.objects.get(id=ex_id, groups__id__contains=group_id)
                rating = Rating(rater=membership, exercise=exercise, comment=ex_comment, proficiency=ex_proficiency)
                rating.save()
                messages.info(request, "Successfully rated exercise \""+ex_name+"\"")

        membership.ratings.add(rating)
        membership.save()

    return HttpResponseRedirect('/syllabus/'+anchor) # Redirect after POST


@login_required
@permission_required('SyllabusTrackerApp.change_exercise', raise_exception=True)
def do_edit_exercises(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
        return membership

    current_page = 0
    if request.method == 'POST':
        data = request.POST
        successful_add = None

        if 'current_page' in data:
            current_page = data['current_page']

        ExerciseFormSet = modelformset_factory(Exercise, form=ExerciseEditForm, can_delete=True, exclude=())
        ex_edit_form = ExerciseFormSet(data)
        if ex_edit_form.is_valid():
            instances = ex_edit_form.save(commit=False)
            for obj in instances:
                for form in ex_edit_form.forms:
                    if form.cleaned_data['id'] == obj:
#                        print("description:"+obj.description)
                        obj.groups.set(form.cleaned_data['groups'], clear=True)
                print("description:"+obj.description)
                obj.save()
            for obj in ex_edit_form.deleted_objects:
                obj.delete()
        else:
            error = "not valid:"
            for err in ex_edit_form.errors:
                error += err.as_text()
            return back_to_editing(request, error, isError=True)

    current_page_string = ""
    if current_page!=0:
        current_page_string = "?exercise_page="+str(current_page)
    return back_to_editing(request, 'Successfully edited!', current_page_string=current_page_string)

@login_required
@permission_required('SyllabusTrackerApp.add_exercise', raise_exception=True)
def do_add_exercise(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    #processing incoming chnges
    if request.method == 'POST':
        data = request.POST
        successful_add = None

        add_ex_input_form = ExerciseForm(data)
        if add_ex_input_form.is_valid():
            if add_ex_input_form.save() != None:
                successful_add = add_ex_input_form.cleaned_data['name']
        else:
            error = "not valid:"
            for err in add_ex_input_form.errors:
                error += err.as_text()
            return back_to_editing(request, error, isError=True)
        
    return back_to_editing(request, 'Successfully added!')

@login_required
@permission_required('SyllabusTrackerApp.add_exercise', raise_exception=True)
def do_add_exercises(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    #processing incoming chnges
    notification = 'Successfully added!'
    isError = False
    if request.method == 'POST':
        data = request.POST
        successful_add = None

        exercise_csv_form = UploadFileForm(data, request.FILES)
        if exercise_csv_form.is_valid():
            feedback = handle_uploaded_file(request.FILES['file'])
            if feedback != None:
                isError = True
                notification = feedback
        else:
            error = "not valid:"
            for err in exercise_csv_form.errors:
                error += err
            return back_to_editing(request, error, isError=True)

    return back_to_editing(request, notification, isError=isError)


@login_required
@permission_required('SyllabusTrackerApp.change_exercisegroup', raise_exception=True)
def do_edit_exercises_groups(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    current_page = 0
    if request.method == 'POST':
        data = request.POST
        successful_add = None

        if 'current_page' in data:
            current_page = data['current_page']

        ExerciseGroupFormSet = modelformset_factory(ExerciseGroup, form=ExerciseGroupForm, can_delete=True, exclude=())
        ex_edit_form = ExerciseGroupFormSet(data)
        if ex_edit_form.is_valid():
            instances = ex_edit_form.save(commit=False)
            for obj in instances:
                obj.save()

            for obj in ex_edit_form.deleted_objects:
                obj.delete()
        else:
            error = "not valid:"
            for err in ex_edit_form.errors:
                error += err.as_text()
            return back_to_editing(request, error, isError=True)

    current_page_string = ""
    if current_page!=0:
        current_page_string = "?exercise_group_page="+str(current_page)
    return back_to_editing(request, 'Successfully edited!', current_page_string=current_page_string)

@login_required
@permission_required('SyllabusTrackerApp.add_exercisegroup', raise_exception=True)
def do_add_exercise_group(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    #processing incoming chnges
    if request.method == 'POST':
        data = request.POST
        successful_add = None

        exercise_group_form = ExerciseGroupForm(data)
        if exercise_group_form.is_valid():
            ex_group = ExerciseGroup(
                    name=exercise_group_form.cleaned_data['name'],
                    description=exercise_group_form.cleaned_data['description']
                )
            ex_group.save()
            ex_group.exercises.set(exercise_group_form.cleaned_data['exercises'])
            ex_group.parent_group = exercise_group_form.cleaned_data['parent_group']
            ex_group.save()

    return back_to_editing(request, 'Successfully added!')

@login_required
@permission_required('SyllabusTrackerApp.change_kyu', raise_exception=True)
def do_add_kyus(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    kyu_form = KyuForm(request.GET)
    if kyu_form.is_valid():
        kyu = Kyu(grade=kyu_form.cleaned_data['grade'], colour=kyu_form.cleaned_data['colour'])
        kyu.save()
    
    KyuFormSet = formset_factory(KyuForm)
    context = {
        'existing_kyu_form':KyuFormSet(initial=Kyu.objects.all().values()),
        'add_kyu_form':KyuForm()
    }
    return render(request, 'SyllabusTrackerApp/add_kyus.html', context)

def send_session_emails(request, session_id):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    try:
        session_instance = Session.objects.get(pk=session_id)
        for atendee in session_instance.attendants.all():
            if not check_setting(atendee, 'receive_session_mail'):
                messages.info(request, "User "+str(atendee)+" opted out of receiving session email.")
                continue

            template_values = atendee.__dict__
            try:
                template_values['instructor'] = session_instance.instructor
                if 'HTTP_HOST' in request.META: 
                    template_values['domain'] = request.META['HTTP_HOST'] 
                else:
                    template_values['domain'] = 'localhost'
                template_values['session'] = session_instance
                msg_plain = render_to_string('session_email.txt', template_values)
                msg_html = render_to_string('session_email.html', template_values)

                send_mail(
                    '[SyllabusTracker] Session review',
                    msg_plain,
                    None,
                    [template_values['email']],
                    html_message=msg_html,
                )
            except:
                messages.error(request, "Problem with email for "+str(template_values['username']))
        messages.info(request, "Emails successfully sent!")
    except:
        messages.error(request, "Couldn't send emails!")

@login_required
@permission_required('SyllabusTrackerApp.change_session', raise_exception=True)
def do_edit_session(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    session_form = SessionForm(request.POST)
    session_id = -1
    try:
        if 'id' in request.POST:
            session_id = request.POST['id']
            session_instance = Session.objects.get(pk=session_id)
            session_form = SessionForm(request.POST, instance=session_instance)
    except:
        pass

    if session_form.is_valid():
        instance = session_form.save()
        if instance!=None:
            session_id = instance.id
            messages.info(request, "Session successfully edited!")
    else:
        error = "not valid:"
        for err in session_form.errors:
            error += err
        messages.error(request, error)

    if session_id != -1 and 'send_attendents_emails' in request.POST:
        send_session_emails(request, session_id)

    return redirect('/sessions/')


