from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import Membership, AppSettings

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

def check_setting(user, setting_name, default=True):
    try:
        settings = AppSettings.objects.get(user=user)
        return settings.__dict__[setting_name]
    except ObjectDoesNotExist:
        pass

    try:
        return AppSettings._meta.get_field(setting_name).get_default()
    except:
        pass

    return default    
