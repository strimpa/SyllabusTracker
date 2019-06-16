from django.shortcuts import redirect
from .models import Membership

def check_membership(user):
    if not user.is_authenticated:
        return redirect('/')
    else:
        try:
            res = Membership.objects.get(user = user)
            #print(str(res))
            return res
        except Exception as e: 
            print(e)
            return redirect('/profile/') # Redirect after POST