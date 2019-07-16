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
from .DisplayLeaf import DisplayLeaf

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
            
        is_summary =  whose != None
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
        group_names = ['Kyu', 'Waza']
        filter = None
        if 'filter' in kwargs and kwargs['filter']!=None:
            filter = kwargs['filter']
            filter = unquote(filter)
            group_names = filter.split(',')
            
        #prefetch leaves
#        start = time.time()
        group_leaves = {} # All end points to attach an exercise to
        group_groups = {} # Grouping of exercise groups that are optional to have an exercise to attach to, i.e. the algorithm shouldn't stop until searching all groups of this group_group
        for name in group_names:
            try:
                group = ExerciseGroup.objects.select_related().get(name=name)
                root_group = group.get_group_root()
                if root_group not in group_groups:
                    group_groups[root_group] = []
                group_groups[root_group].append(name)
                group_leaves[name] = group.collect_leaves()
            except:
                messages.info(request, "Exercise Group not found:"+name)
                return redirect('/syllabus/')
                pass

#        end = time.time()
 #       print("time for group prefretch:"+str(end - start))

        display_root = DisplayLeaf("Display root", 0)
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
            ordered_groups = {}
#            print (str(ex))
            #create the tree of sub groups
            current_root = display_root
            all_groups_in_filter = True
            for group_group_root in group_groups:
                for name in group_groups[group_group_root]:
                    leaves = group_leaves[name]
                    for group in ex.groups.all():
                        if group in leaves:
    #                        print("appending "+str(group))
                            group_leaf = DisplayLeaf.find_or_create_leaf(group, current_root, current_root.depth+1)
                            current_root = group_leaf
                            append_exercise = name == group_names[-1]
                            if append_exercise:
                                group_leaf.exercises.append((ex, rating))  
                    
                #Break to next exercise if the first group in the exercise has not been found in any root group defined in filter
                if current_root == display_root:
                    break

#            ex3 = time.time()
#            print("time 2:"+str(ex3 - ex2))


#        end2 = time.time()
#        print("time for exercise processing:"+str(end2 - end))

        display_root.enumerate_hier(0,"", 0)
#        display_root.print_hier(0)
                
        context = {
            'title':"Syllabus",
            'display_root': display_root,
            'depth':5,
            'is_summary':is_summary,
            'whose':whose,
            'selected_memberships':selected_memberships,
            'all_memberships':all_memberships,
            'filter':filter
        }
        return render(request, 'SyllabusTrackerApp/syllabus.html', context)
