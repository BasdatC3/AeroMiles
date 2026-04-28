from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'})
    )


class MemberRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    salutation = forms.CharField(max_length=10, required=False)
    first_mid_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    country_code = forms.CharField(max_length=5, required=False)
    phone = forms.CharField(max_length=20, required=False)
    nationality = forms.CharField(max_length=100, required=False)
    birth_date = forms.DateField(required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_mid_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.role = 'member'
        if commit:
            user.save()
        return user


class StaffRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    salutation = forms.CharField(max_length=10, required=False)
    first_mid_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    country_code = forms.CharField(max_length=5, required=False)
    phone = forms.CharField(max_length=20, required=False)
    nationality = forms.CharField(max_length=100, required=False)
    birth_date = forms.DateField(required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = 'staf'
        if commit:
            user.save()
        return user