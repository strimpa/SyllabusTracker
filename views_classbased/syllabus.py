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
from .DisplayLeaf import DisplayLeaf, ExerciseStudentSummary

class SyllabusView(View):

    def get_ratings(self, membership, is_summary, memberships):
        ratings_by_exercise = {}
        if is_summary:
            all_ratings = Rating.objects.select_related().filter(rater__in = memberships).order_by("-rate_date")
            for r in all_ratings:
                if not check_setting(r.rater.user, 'ratings_are_public'):
                    continue

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

        do_redirect = False
        whose = None
        if 'whose' in request.GET:
            whose = ','.join(request.GET.getlist('whose'))
            do_redirect = True
        #analyse for participating ratings
        elif 'whose' in kwargs and kwargs['whose']!="" and kwargs['whose']!="None":
            whose = kwargs['whose']
            
        filter = None
        if 'filter' in request.GET:
            filter = ','.join(request.GET.getlist('filter'))
            do_redirect = True
        elif 'filter' in kwargs and kwargs['filter']!=None and kwargs['filter']!="None":
            filter = kwargs['filter']
            filter = unquote(filter)

        if do_redirect:
            return redirect('syllabus', whose=whose, filter=filter)

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
        groups = ExerciseGroup.objects.select_related().order_by("list_order_index")
        group_names = ['Kyu', 'Waza']

        # Always load these two for filtering
        all_group_groups = {} # Grouping of exercise groups that are optional to have an exercise to attach to, i.e. the algorithm shouldn't stop until searching all groups of this group_group
        for name in group_names:
            group = groups.get(name=name)
            root_group = group.get_group_root()

            if root_group.name not in all_group_groups:
                all_group_groups[root_group.name] = root_group.get_children()

        # replace actually used ones with the incoming user selection
        if filter != None:
            group_names = filter.split(',')
        #default to user's kyu, if available
        elif membership.kyu != None:
            theKyu = membership.kyu
            try:
                theKyu = Kyu.objects.get(grade=theKyu.grade+1)
            except:
                pass
            group_names[0] = theKyu.colour
            
        # Prefetch leaves
        group_leaves = {} # All end points to attach an exercise to
        selected_group_groups = {} # Grouping of exercise groups that are optional to have an exercise to attach to, i.e. the algorithm shouldn't stop until searching all groups of this group_group
        for name in group_names:
            try:
                group = groups.get(name=name)
                root_group = group.get_group_root()

                if root_group.name not in selected_group_groups:
                    selected_group_groups[root_group.name] = []
                selected_group_groups[root_group.name].append(name)

                group_leaves[name] = group.collect_leaves()
            except:
                messages.info(request, "Exercise Group not found:"+name)
                print ("*** Exercise Group not found:"+name+"!")
                return redirect('/syllabus/filter-None')

        display_root = DisplayLeaf("Display root", 0)
        depth = 0
        exercises = Exercise.objects.select_related().order_by("list_order_index")

        
        rating_values_by_exercise = {}
        if is_summary:
            rating_values_by_exercise = {x:ratings_by_exercise[x].rating_average for x in ratings_by_exercise }
        else:
            rating_values_by_exercise = {x:ratings_by_exercise[x].proficiency for x in ratings_by_exercise }
        
        for x in exercises:
            if not x.name in rating_values_by_exercise:
                rating_values_by_exercise[x.name] = -1

        exercises = sorted(exercises, key=lambda ex: rating_values_by_exercise[ex.name])

        for ex in exercises:
            rating = None
            try:
                rating = ratings_by_exercise[ex.name]
            except:
                pass
            
            # for each group this exercise is in, 
            this_groups = ex.groups.all()
            ordered_groups = {}
            #create the tree of sub groups
            current_root = display_root
            all_groups_in_filter = True
            for group_group_root in selected_group_groups:
                for name in selected_group_groups[group_group_root]:
                    leaves = group_leaves[name]
                    for group in ex.groups.all():
                        if group in leaves:
                            group_leaf = DisplayLeaf.find_or_create_leaf(group, current_root, current_root.depth+1)
                            current_root = group_leaf
                            append_exercise = name == group_names[-1]
                            if append_exercise:
                                group_leaf.exercises.append((ex, rating))  
                    
                #Break to next exercise if the first group in the exercise has not been found in any root group defined in filter
                if current_root == display_root:
                    break

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
            'selected_group_groups':selected_group_groups,
            'all_group_groups':all_group_groups,
            'filter':filter
        }
        return render(request, 'SyllabusTrackerApp/syllabus.html', context)
