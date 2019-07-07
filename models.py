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
    description = models.CharField(max_length=1024, blank=True)
    exercises = models.ManyToManyField(Exercise, blank=True, related_name="groups")
    parent_group = models.ForeignKey("ExerciseGroup", on_delete=models.SET_NULL, blank=True, null=True, related_name="child_groups")
    show_in_hierarchy = models.BooleanField(default=True)
    list_order_index = models.IntegerField(default=0)
    
    def __str__(self):
       return self.name

    def get_group_root(self):
        if None != self.parent_group:
            return self.parent_group.get_group_root()
        else:
            return self

    def collect_leaves(self):
        these_leaves = []
        if len(list(self.exercises.all()))>0:
            these_leaves.append(self)
        for child in list(self.child_groups.all()):
            these_leaves += child.collect_leaves()
        return these_leaves

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

class Jitsuka(AbstractUser):
    def __str__(self):
       return self.username 

    def full_name(self):
        return (self.first_name + " " + self.last_name + " (" + self.username + ")")

    def is_instructor(self):
        return self.groups.filter(name="Instructors").exists()

    def is_assistent_instructor(self):
        return self.groups.filter(name="Assistent Instructors").exists()

    def is_assistent_instructor_or_instructor(self):
        return self.groups.filter(name__endswith="Instructors").exists()

class Membership(models.Model):
    user = models.ForeignKey(Jitsuka, null=True, on_delete=models.CASCADE, related_name="membership")
    memberID = models.IntegerField()
    pic = models.ImageField(height_field=1000, width_field=1000, max_length=256, null=True, blank=True)
    kyu = models.ForeignKey(Kyu, on_delete=models.SET_NULL, blank=True, null=True)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, blank=True, null=True)
    instructor = models.ForeignKey('Jitsuka', models.SET_NULL, blank=True, null=True, related_name="student")
    sign_up_date = models.DateField(auto_now_add=True)
    leaving_date = models.DateField(auto_now_add=False, null=True, blank=True)
    insurance_expiry_date = models.DateField(auto_now_add=False, null=True, blank=True)
    
    def __str__(self):
       return (self.user.username + ":" + str(self.memberID))

class RegistrationRequest(models.Model):
    user = models.ForeignKey(Jitsuka, on_delete=models.CASCADE)
    guid = models.CharField(max_length=64)
    request_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return (self.user.full_name() + ":" +str(self.request_date) + ":" +self.guid)

class Rating(models.Model):
    PROFICIENCY_LEVEL = (
        ('S', 'seen'),
        ('A', 'attempted'),
        ('U', 'understood'),
        ('P', 'proficient')
    )
    PROFICIENCY_TOKENS = (
        'S', 'A', 'U', 'P'
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    comment = models.CharField(max_length=60)
    proficiency = models.CharField(max_length=1, choices=PROFICIENCY_LEVEL)
    rate_date = models.DateTimeField(auto_now_add=True)
    rater = models.ForeignKey(Membership, related_name="ratings", on_delete=models.CASCADE)
    
    def __str__(self):
        if self.exercise == None:
            return "Invalid rating!"
        return (self.exercise.name + ":" + self.proficiency)

class Session(models.Model):
    date = models.DateTimeField()
    attendants = models.ManyToManyField(Jitsuka, related_name="attended_sessions")
    exercises = models.ManyToManyField(ExerciseGroup)
    instructor = models.ForeignKey(Jitsuka, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    
    def __str__(self):
       return (str(self.date) + " - " + self.instructor.full_name())
