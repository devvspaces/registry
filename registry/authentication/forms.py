from django import forms
from django.contrib.auth import password_validation

from .models import User


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        min_length=8,
        help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
        help_text='Must be similar to first password to pass verification')

    class Meta:
        model = User
        fields = ("email", "password", "password2",)

    def clean_password(self):
        ps1 = self.cleaned_data.get("password")
        password_validation.validate_password(ps1, None)
        return ps1

    def clean_password2(self):
        ps1 = self.cleaned_data.get("password")
        ps2 = self.cleaned_data.get("password2")
        if (ps1 and ps2) and (ps1 != ps2):
            raise forms.ValidationError("The passwords does not match")
        return ps2

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get("password"))
        if commit:
            user.save()
        return user
