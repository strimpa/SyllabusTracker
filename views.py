#from django.shortcuts import render

# Create your views here.
from .models import Excercise
from django.http import HttpResponse
from django.shortcuts import render
	
def index(request):
#    return HttpResponse("You're looking at question ")
    latest_question_list = Excercise.objects.all()[:5]
    context = {'all_excercises': latest_question_list}
    return render(request, 'SyllasbusTrackerApp/index.html', context)