from django.db import models
from django.contrib.auth.models import AbstractUser

# A trainable unit
class Exercise(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1024)
    pic = models.ImageField(height_field=1000, width_field=1000, max_length=256, null=True, blank=True)
    list_order_index = models.IntegerField(default=0)
    
    def __str__(self):
       return self.name
    
    def to_table_row(self):
        return "<tr><td>"+self.name+"</td><td>"+self.description+"</td></tr>"

# An association between exercises
class ExerciseGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1024)
    exercises = models.ManyToManyField(Exercise, blank=True)
    parent_group = models.ForeignKey("ExerciseGroup", on_delete=models.SET_NULL, blank=True, null=True)
    show_in_hierarchy = models.BooleanField(default=True)
    list_order_index = models.IntegerField(default=0)
    
    def __str__(self):
       return self.name

    def get_group_root(self):
        if None != self.parent_group:
            return self.parent_group.get_group_root()
        else:
            return self

class Kyu(models.Model):
    grade = models.IntegerField()
    colour = models.CharField(max_length=60)
    
    def __str__(self):
       return self.colour

class Club(models.Model):
    abreviation = models.CharField(max_length=8)
    name = models.CharField(max_length=60)
    
    def __str__(self):
       return self.name

class Rating(models.Model):
    PROFICIENCY_LEVEL = (
        ('S', 'seen'),
        ('A', 'attempted'),
        ('U', 'understood'),
        ('P', 'proficient')
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, blank=True, null=True)
    comment = models.CharField(max_length=60)
    proficiency = models.CharField(max_length=1, choices=PROFICIENCY_LEVEL)
    rate_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
       return (self.exercise.name + ":" + self.proficiency)

class Jitsuka(AbstractUser):
    user_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=256)
    
    def __str__(self):
       return self.username 

    def full_name(self):
        return (first_name + " " + last_name)

class Membership(models.Model):
    user = models.ForeignKey(Jitsuka, null=True, on_delete=models.CASCADE, related_name="%(class)s_membership_user")
    memberID = models.IntegerField()
    pic = models.ImageField(height_field=1000, width_field=1000, max_length=256, null=True)
    kyu = models.ForeignKey(Kyu, on_delete=models.SET_NULL, blank=True, null=True)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, blank=True, null=True)
    is_senior = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    instructor = models.ForeignKey('Jitsuka', models.SET_NULL, blank=True, null=True)   
    sign_up_date = models.DateField(auto_now_add=True)
    leaving_date = models.DateField(auto_now_add=False, null=True)
    insurance_expiry_date = models.DateField(auto_now_add=False, null=True)
    ratings = models.ManyToManyField(Rating)
    
    def __str__(self):
       return (self.user.full_name + ":" +str(memberID))

class Session(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    attendants = models.ManyToManyField(Jitsuka, related_name="%(class)s_session_attendants")
    exercises = models.ManyToManyField(ExerciseGroup)
    instructor = models.ForeignKey(Jitsuka, on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
       return (self.date + " - " + self.instructor.full_name)
