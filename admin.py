from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Jitsuka, Membership, Excercise, ExcerciseGroup, Session, Kyu, Club

# Register your models here.

admin.site.register(Jitsuka, UserAdmin)
admin.site.register(Excercise)
admin.site.register(Session)
admin.site.register(Kyu)
admin.site.register(Membership)
admin.site.register(ExcerciseGroup)
admin.site.register(Club)