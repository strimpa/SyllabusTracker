from django import forms
from django.forms import ModelForm
from .models import (Jitsuka, Exercise, Membership, Kyu, ExerciseGroup, Session)

MAX_USERNAME_LENGTH = 100

class LoginForm(forms.Form):
    username = forms.CharField(max_length=MAX_USERNAME_LENGTH)
    password = forms.CharField(widget=forms.PasswordInput(render_value=True))

class ProfileForm(ModelForm):
    class Meta:
        model = Jitsuka
        fields = ['first_name', 'last_name', 'email']
    username = forms.CharField(widget=forms.HiddenInput, required=False)

class RegisterForm(ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    class Meta:
        model = Jitsuka
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class ImageForm(forms.Form):
    pic = forms.ImageField()

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'description', 'pic']

class ExerciseEditForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = '__all__'

class MembershipForm(ModelForm):
    class Meta:
        model = Membership
        exclude = ['user', 'ratings', 'leaving_date', 'insurance_expiry_date']
    membership_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    user_id = forms.IntegerField(widget=forms.HiddenInput)
    insurance_expiry = forms.DateField(disabled=True, required=False)

class UploadFileForm(forms.Form):
    file = forms.FileField()

class KyuForm(ModelForm):
    class Meta:
        model = Kyu
        fields = '__all__'

class ExerciseGroupForm(ModelForm):
    class Meta:
        model = ExerciseGroup
        #fields = '__all__'
        exclude = ['exercises']

class SessionForm(ModelForm):
    class Meta:
        model = Session
        fields = '__all__'
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)

class ReadOnlyFormMixin(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReadOnlyFormMixin, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].disabled = True

    def save(self, *args, **kwargs):
        # do not do anything
        pass

class SessionFormReadOnly(ReadOnlyFormMixin, SessionForm):
    pass