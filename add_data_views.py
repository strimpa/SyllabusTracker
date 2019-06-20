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
def back_to_editing(request, notification, isError=False):
    if isError:
        messages.error(request, notification)
    else:
        messages.info(request, notification)
    return redirect('/exercise_editing/')

@login_required
def rate(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    #processing incoming rating
    if request.method == "POST":
        data = request.POST
        exercise = Exercise.objects.get(name=data['exercise_name'])
        rating = Rating(rater=membership, exercise=exercise, comment=data['comment'], proficiency=data['proficiency'])
        rating.save()

        membership.ratings.add(rating)
        membership.save()
        messages.info(request, "Successfully rated exercise \""+exercise.name+"\"")

    return HttpResponseRedirect('/syllabus/') # Redirect after POST


@login_required
@permission_required('SyllabusTrackerApp.change_exercise', raise_exception=True)
def edit_exercises(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
        return membership

    if request.method == 'POST':
        data = request.POST
        successful_add = None

        ExerciseFormSet = modelformset_factory(Exercise, form=ExerciseEditForm, can_delete=True, exclude=())
        ex_edit_form = ExerciseFormSet(data)
        if ex_edit_form.is_valid():
            instances = ex_edit_form.save(commit=False)
            for obj in instances:
                messages.info(obj.name+" parent group:"+str(obj.parent_group))
                obj.save()
            for obj in ex_edit_form.deleted_objects:
                obj.delete()
            return back_to_editing(request, 'Successfully edited!')
        else:
            error = "not valid:"
            for err in ex_edit_form.errors:
                error += err.as_text()
            return back_to_editing(request, error, isError=True)
    
    return HttpResponseRedirect('/exercise_editing/') # Redirect after POST

@login_required
@permission_required('SyllabusTrackerApp.add_exercise', raise_exception=True)
def add_exercise(request):
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
def add_exercises(request):
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
def edit_exercises_groups(request):
    membership = check_membership(request.user)
    if isinstance(membership, HttpResponse):
       return membership

    if request.method == 'POST':
        data = request.POST
        successful_add = None

        ExerciseGroupFormSet = modelformset_factory(ExerciseGroup, form=ExerciseEditForm, can_delete=True, exclude=())
        ex_edit_form = ExerciseGroupFormSet(data)
        if ex_edit_form.is_valid():
            instances = ex_edit_form.save(commit=False)
            print("instances changed:"+str(len(instances)))
            for obj in instances:
                for form in ex_edit_form.forms:
                    if form.cleaned_data['id'] == obj:
#                        print("description:"+obj.description)
                        obj.exercises.set(form.cleaned_data['exercises'], clear=True)
                print("description:"+obj.description)
                obj.save()

            for obj in ex_edit_form.deleted_objects:
                obj.delete()
        else:
            error = "not valid:"
            for err in ex_edit_form.errors:
                error += err.as_text()
            return back_to_editing(request, error, isError=True)

    return back_to_editing(request, 'Successfully edited!')

@login_required
@permission_required('SyllabusTrackerApp.add_exercisegroup', raise_exception=True)
def add_exercise_group(request):
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
def add_kyus(request):
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

@login_required
@permission_required('SyllabusTrackerApp.add_session', raise_exception=True)
def edit_sessions(request):
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
