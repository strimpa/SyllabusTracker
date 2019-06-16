from django.shortcuts import redirect
from .models import Membership

def check_membership(user, fail_redirect="/profile/"):
    if not user.is_authenticated:
        return redirect('/')
    else:
        try:
            res = Membership.objects.get(user = user)
            print(str(res))
            return res
        except Exception as e: 
            print("Exception:"+str(e)+" for "+str(user))
            return redirect(fail_redirect) # Redirect after POST