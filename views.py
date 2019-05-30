#from django.shortcuts import render

# Create your views here.
from .models import Exercise, Session, Rating, Membership, Kyu, ExerciseGroup
from .forms import LoginForm, ExerciseForm, ExerciseEditForm, UploadFileForm, KyuForm, ExerciseGroupForm
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/user_home/') # Redirect after POST
    next = '/user_home/'
    if 'next' in request.GET:
        next = request.GET['next']
    return render(request, 'SyllabusTrackerApp/index.html', 
        {
            'login_form':LoginForm(),
            'target_url':next
        })

def check_membership(user):
    if not user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        try:
            return Membership.objects.get(user = user)
        except:
            return HttpResponseRedirect('/profile/') # Redirect after POST

@login_required
def home(request):
    check_membership(request.user)  

    latest_session_list = Session.objects.all()[:5]
    context = {
        'latest_session_list': latest_session_list,
        'login_form':LoginForm()
    }
    return render(request, 'SyllabusTrackerApp/home.html', context)

class DisplayLeaf():
    def __init__(self, name, show_in_hierarchy, list_order_index, depth):
        self.name = name
        self.children = []
        self.exercises = []
        self.parent_leaf = None
        self.show_in_hierarchy = show_in_hierarchy
        self.list_order_index = list_order_index
        self.depth = depth
    
    def __str__(self):
        return "DisplayLeaf:"+self.name

def find_leaf(leaf_name, root):
    if root.name == leaf_name:
        return root
    if hasattr(root, "children"):
        for child in root.children:
            found = find_leaf(leaf_name, child)
            if found != None:
                return found
    return None

def print_hier(leaf, depth):
    output = ""
    for i in range(depth):
        output += ("\t")
    output += leaf.name
    if hasattr(leaf, "depth"):
        output += ", "+str(leaf.depth)
    print(output)
    if hasattr(leaf, "children"):
        for c in leaf.children:
            print_hier(c, depth+1)
    if hasattr(leaf, "exercises"):
        for c, r in leaf.exercises:
            print_hier(c, depth+1)

def find_or_create_leaf(group, group_root, curr_depth):
    display_leaf = find_leaf(group.name, group_root)
    if display_leaf == None:
        display_leaf = DisplayLeaf(group.name, group.show_in_hierarchy, group.list_order_index, curr_depth)

    root_leaf = group_root
    parent_leaf = group_root
    if group.parent_group != None:
        parent_leaf = find_or_create_leaf(group.parent_group, group_root, curr_depth+1)
    
    if not display_leaf in parent_leaf.children:
        curr_index = 0
        for c in parent_leaf.children:
            if c.list_order_index>=curr_index:
                break
            curr_index+=1
        parent_leaf.children.insert(curr_index, display_leaf)
    return display_leaf

@login_required
# Shoowing the syllabus with the user's ratings
def syllabus(request):
    membership = check_membership(request.user)
 
    all_exercises = []
    my_ratings = membership.ratings.all()
    groups = ExerciseGroup.objects.all()
    #find groups per order
    root_group_names = ['Kyu', 'Waza']  

    display_root = DisplayLeaf("Display root", False, 0, 1)
    depth = 0
    for ex in Exercise.objects.order_by("list_order_index"):
        rating = None
        try:
            rating = my_ratings.filter(exercise=ex).order_by("-rate_date")[0]
        except:
            pass
        
        # for each groups this exercise is in, create the tree of sub groups
        this_groups = ex.exercisegroup_set.all()
        ordered_groups = []
        for name in root_group_names:
            for group in ex.exercisegroup_set.all():
                my_root_group = group.get_group_root()
                if my_root_group.name == name:
                    ordered_groups.append(group)

        current_root = display_root
        for ex_group in ordered_groups:
            print ("exercise:"+ex.name+" ex_group.name:"+ex_group.name+" current_root:"+str(current_root))
            # create copies for child groups
            group_leaf = find_or_create_leaf(ex_group, current_root, current_root.depth)
            print("found or created root leaf "+group_leaf.name)
            current_root = group_leaf
            append_exercise = ex_group == ordered_groups[-1]
            if append_exercise:
                group_leaf.exercises.append((ex, rating))
        
    print_hier(display_root, 0)
            
    context = {
        'display_root': display_root,
        'depth':5
    }
    return render(request, 'SyllabusTrackerApp/syllabus.html', context)

@login_required
def exercise_editing(request, successful_add=False):
    membership = check_membership(request.user)

    all_groups = ExerciseGroup.objects.all()
    ExerciseGroupFormSet = modelformset_factory(ExerciseGroup, form=ExerciseGroupForm, can_delete=True, exclude=(), extra=0)
    ExerciseFormSet = modelformset_factory(Exercise, form=ExerciseEditForm, can_delete=True, exclude=(), extra=0)

    add_ex_form = ExerciseForm()
    exercise_csv_form = UploadFileForm()
    ex_edit_form = ExerciseFormSet(initial=Exercise.objects.all().values())
    context = {
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
def add_kyus(request):
    membership = check_membership(request.user)

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
