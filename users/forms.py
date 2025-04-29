from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')

class SignupStep1Form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'age', 'profession', 'profession_detail', 'bio', 'hobbies')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and age < 18:
            raise forms.ValidationError("You must be at least 18 years old to register.")
        return age

class SignupStep2Form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email',)

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, min_length=6, required=True, 
                          widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit OTP'}))

class LoginForm(forms.Form):
    email = forms.EmailField(required=True, 
                             widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
