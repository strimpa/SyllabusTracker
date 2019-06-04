from django.shortcuts import redirect
from .models import Membership

def check_membership(user):
    if not user.is_authenticated:
        return redirect('/')
    else:
        try:
            return Membership.objects.get(user = user)
        except:
            return redirect('/profile/') # Redirect after POST