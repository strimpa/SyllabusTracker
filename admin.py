from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Jitsuka, Membership, Exercise, ExerciseGroup, Session, Kyu, Club, Notification, FeeDefinition

# Register your models here.

admin.site.register(Jitsuka, UserAdmin)
admin.site.register(Exercise)
admin.site.register(Session)
admin.site.register(Kyu)
admin.site.register(Membership)
admin.site.register(ExerciseGroup)
admin.site.register(Club)
admin.site.register(Notification)
admin.site.register(FeeDefinition)