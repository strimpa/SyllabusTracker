from django.db import models
from django.contrib.auth.models import AbstractUser

# A trainable unit
class Excercise(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1024)
    pic = models.ImageField(height_field=1000, width_field=1000, max_length=256)
	
# An association between excercises
class ExcerciseGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1024)
    excercises = models.ManyToManyField(Excercise)

class Kyu(models.Model):
    grade = models.IntegerField()
    colour = models.CharField(max_length=60)
    
    def __str__(self):
       return self.colour

class Club(models.Model):
    abreviation = models.CharField(max_length=8)
    name = models.CharField(max_length=60)

class Rating(models.Model):
    PROFICIENCY_LEVEL = (
        ('S', 'seen'),
        ('A', 'attempted'),
        ('U', 'understood'),
        ('P', 'proficient')
    )
    excercise = models.ForeignKey(Excercise, on_delete=models.SET_NULL, blank=True, null=True)
    comment = models.CharField(max_length=60)
    proficiency = models.CharField(max_length=1, choices=PROFICIENCY_LEVEL)
    rate_date = models.DateField(auto_now_add=True)

class Jitsuka(AbstractUser):
    user_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=256)

class Membership(models.Model):
    user = models.ForeignKey(Jitsuka, null=True, on_delete=models.CASCADE, related_name="%(class)s_membership_user")
    memberID = models.IntegerField()
    pic = models.ImageField(height_field=1000, width_field=1000, max_length=256, null=True)
    kyu = models.ForeignKey(Kyu, on_delete=models.SET_NULL, blank=True, null=True)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, blank=True, null=True)
    is_senior = models.BooleanField()
    is_instructor = models.BooleanField()
    instructor = models.ForeignKey('Jitsuka', models.SET_NULL, blank=True, null=True)
    sign_up_date = models.DateField(auto_now_add=True)
    leaving_date = models.DateField(auto_now_add=False, null=True)
    insurance_expiry_date = models.DateField(auto_now_add=False, null=True)
    ratings = models.ManyToManyField(Rating)

class Session(models.Model):
    date = models.DateField(auto_now_add=True)
    attendants = models.ManyToManyField(Jitsuka, related_name="%(class)s_session_attendants")
    excercises = models.ManyToManyField(ExcerciseGroup)
    instructor = models.ForeignKey(Jitsuka, on_delete=models.SET_NULL, blank=True, null=True)
