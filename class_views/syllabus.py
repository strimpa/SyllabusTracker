from ..models import Exercise, Session, Rating, Membership, Kyu, ExerciseGroup
from ..forms import LoginForm, ExerciseForm, ExerciseEditForm, UploadFileForm, KyuForm, ExerciseGroupForm
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from ..view_utils import *


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
        return "DisplayLeaf:"+self.name+": "+str(self.depth)

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

def find_or_create_leaf(group, group_root, root_depth):
    display_leaf = find_leaf(group.name, group_root)
    if display_leaf == None:
        display_leaf = DisplayLeaf(group.name, group.show_in_hierarchy, group.list_order_index, root_depth)

    root_leaf = group_root
    parent_leaf = group_root
    if group.parent_group != None:
        parent_leaf = find_or_create_leaf(group.parent_group, group_root, root_depth)
        #only increase the depth if the leaf is shown in hierarchy
        if parent_leaf.show_in_hierarchy:
            display_leaf.depth = parent_leaf.depth+1
    
    if not display_leaf in parent_leaf.children:
        curr_index = 0
        for c in parent_leaf.children:
            if c.list_order_index>=curr_index:
                break
            curr_index+=1
        parent_leaf.children.insert(curr_index, display_leaf)
    return display_leaf

class ExerciseStudentSummary():
    def __init__(self, name):
        self.name = name
        self.students_ratings = {}
        self.rating_average = 0
    def __str__(self):
        return self.name+"average:"+str(self.rating_average)

class SyllabusView(View):

    def get_ratings(self, membership, memberships):
        ratings_by_exercise = {}
        if len(memberships)>1:
            all_ratings = Rating.objects.select_related().filter(rater__in = memberships)
            print("all_ratings:"+str(len(all_ratings)))
            for r in all_ratings:
                if r.exercise != None:
                    # Initialise exercise summary
                    if r.exercise.name not in ratings_by_exercise:
                        ratings_by_exercise[r.exercise.name] = ExerciseStudentSummary(r.exercise.name)

                    # Only append first rating for each exercise per user
                    username = r.rater.user.username
                    if username not in ratings_by_exercise[r.exercise.name].students_ratings:
                        print(username+" rated "+r.exercise.name+" with " + r.proficiency)
                        ratings_by_exercise[r.exercise.name].students_ratings[username] = r.proficiency

            # Average out
            for rating in ratings_by_exercise.values():
                rating.rating_average = 0.0
                for student_rating in rating.students_ratings.values():
                    rating_index = Rating.PROFICIENCY_TOKENS.index(student_rating)
                    rating.rating_average += rating_index
                number_ratings = len(rating.students_ratings)
                rating.rating_average /= number_ratings
        else:
            my_ratings = memberships[0].ratings.all().order_by("-rate_date")
            for r in my_ratings:
                if r.exercise != None: 
                    if r.exercise.name not in ratings_by_exercise:
                        ratings_by_exercise[r.exercise.name] = r
        return ratings_by_exercise

    @method_decorator(login_required)
    # Showing the syllabus with the user's ratings       
    def get(self, request, *args, **kwargs):
        membership = check_membership(request.user)           
        if isinstance(membership, HttpResponse):
            return membership
        
        is_summary = 'whose' in kwargs and kwargs['whose'] == "my_students" and request.user.is_assistent_instructor_or_instructor()
        memberships = [membership]
        if is_summary:
            my_club = membership.club
            memberships = Membership.objects.filter(club = my_club)

        ratings_by_exercise = self.get_ratings(membership, memberships)
        groups = ExerciseGroup.objects.all()
        #find groups per order
        root_group_names = ['Kyu', 'Waza']  

        display_root = DisplayLeaf("Display root", False, 0, 0)
        depth = 0
        for ex in Exercise.objects.order_by("list_order_index"):
            rating = None
            try:
                rating = ratings_by_exercise[ex.name]
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
                # create copies for child groups
                group_leaf = find_or_create_leaf(ex_group, current_root, current_root.depth+1)
                current_root = group_leaf
                append_exercise = ex_group == ordered_groups[-1]
                if append_exercise:
                    group_leaf.exercises.append((ex, rating))  
            
 #       print_hier(display_root, 0)
                
        context = {
            'title':"Syllabus",
            'display_root': display_root,
            'depth':5,
            'is_summary':is_summary
        }
        return render(request, 'SyllabusTrackerApp/syllabus.html', context)
