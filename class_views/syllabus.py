from urllib.parse import unquote
import time

from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe

from ..models import Exercise, Session, Rating, Membership, Kyu, ExerciseGroup
from ..forms import LoginForm, ExerciseForm, ExerciseEditForm, UploadFileForm, KyuForm, ExerciseGroupForm
from ..view_utils import *

class DisplayLeaf():
    def __init__(self, name, id, show_in_hierarchy, list_order_index, depth):
        self.name = name
        self.id = id
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
        output += ("   ")
    output += "'"+leaf.name+"'"
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
        display_leaf = DisplayLeaf(group.name, group.id, group.show_in_hierarchy, group.list_order_index, root_depth)
        if group.parent_group != None:
            display_leaf.parent_leaf = find_or_create_leaf(group.parent_group, group_root, root_depth)
            #only increase the depth if the leaf is shown in hierarchy
            if display_leaf.parent_leaf.show_in_hierarchy:
                display_leaf.depth = display_leaf.parent_leaf.depth+1
        else:
            display_leaf.parent_leaf = group_root

    if not display_leaf in display_leaf.parent_leaf.children:
        curr_index = 0
        for c in display_leaf.parent_leaf.children:
            if c.list_order_index>=curr_index:
                break
            curr_index+=1
        display_leaf.parent_leaf.children.insert(curr_index, display_leaf)
    return display_leaf

class ExerciseStudentSummary():
    def __init__(self, name):
        self.name = name
        self.students_ratings = {}
        self.rating_average = 0
    def __str__(self):
        return self.name+"average:"+str(self.rating_average)

class SyllabusView(View):

    def get_ratings(self, membership, is_summary, memberships):
        ratings_by_exercise = {}
        if is_summary:
            all_ratings = Rating.objects.select_related().filter(rater__in = memberships)
#            print("all_ratings:"+str(len(all_ratings)))
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
        
        #analyse for participating ratings
        whose = None
        if 'whose' in kwargs and kwargs['whose']!="" and kwargs['whose']!="None":
            whose = kwargs['whose']

        if 'user_select_whose' in request.GET:
            whose = ','.join(request.GET.getlist('user_select_whose'))
            
        is_summary =  whose != None and request.user.is_assistent_instructor_or_instructor()
        selected_memberships = [membership]
        all_memberships = []
        if is_summary:
            my_club = membership.club
            all_memberships = Membership.objects.filter(club = my_club)
            if whose=="my_club":
                selected_memberships = all_memberships
            else:
                name_list = whose.split(',')
                selected_memberships = Membership.objects.filter(user__username__in = name_list)

    
        #find groups per order
        ratings_by_exercise = self.get_ratings(membership, is_summary, selected_memberships)
        groups = ExerciseGroup.objects.all()
        root_group_names = ['Kyu', 'Waza']
        order = None
        if 'order' in kwargs and kwargs['order']!=None:
            order = kwargs['order']
            order = unquote(order)
            root_group_names = order.split(',')
            
        #prefetch leaves
#        start = time.time()
        root_group_leaves = {}
        former_root_groups = []
        for name in root_group_names:
            try:
                group = ExerciseGroup.objects.select_related().get(name=name)
                root_group = group.get_group_root()
                if root_group in former_root_groups:
                    messages.info(request, "Exercise Group "+name+" has the same root as the former passed group!")
                    continue
                root_group_leaves[name] = group.collect_leaves()
                former_root_groups.append(root_group)
            except:
                messages.info(request, "Exercise Group not found:"+name)
                return redirect('/syllabus/')
                pass

#        end = time.time()
 #       print("time for group prefretch:"+str(end - start))

        display_root = DisplayLeaf("Display root", 0, False, 0, 0)
        depth = 0
        for ex in Exercise.objects.select_related().order_by("-list_order_index"):
            ex1 = time.time()
            rating = None
            try:
                rating = ratings_by_exercise[ex.name]
            except:
                pass
            
            # for each group this exercise is in, 
            this_groups = ex.groups.all()
            ordered_groups = []
#            print (str(ex))
            for name in root_group_names:
                leaves = root_group_leaves[name]
                for group in ex.groups.all():
                    if group in leaves:
#                        print("appending "+str(group))
                        ordered_groups.append(group)

#            ex2 = time.time()
#            print("time 1:"+str(ex2 - ex1))

            if len(ordered_groups) == len(root_group_names):
                #create the tree of sub groups
                current_root = display_root
                for ex_group in ordered_groups:
                    # create copies for child groups
                    group_leaf = find_or_create_leaf(ex_group, current_root, current_root.depth+1)
                    current_root = group_leaf
                    append_exercise = ex_group == ordered_groups[-1]
                    if append_exercise:
                        group_leaf.exercises.append((ex, rating))  
#            ex3 = time.time()
#            print("time 2:"+str(ex3 - ex2))


#        end2 = time.time()
#        print("time for exercise processing:"+str(end2 - end))

#        print_hier(display_root, 0)
                
        context = {
            'title':"Syllabus",
            'display_root': display_root,
            'depth':5,
            'is_summary':is_summary,
            'whose':whose,
            'selected_memberships':selected_memberships,
            'all_memberships':all_memberships,
            'order':order
        }
        return render(request, 'SyllabusTrackerApp/syllabus.html', context)
