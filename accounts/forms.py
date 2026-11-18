from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


def check_school_email(email, exclude_pk=None):
    """Require the school email domain and a unique (case-insensitive) email."""
    email = email.strip().lower()
    domain = settings.ALLOWED_EMAIL_DOMAIN
    if not email.endswith('@' + domain):
        raise forms.ValidationError(f'Please use your @{domain} school email.')
    taken = CustomUser.objects.filter(email__iexact=email)
    if exclude_pk:
        taken = taken.exclude(pk=exclude_pk)
    if taken.exists():
        raise forms.ValidationError('An account with this email already exists.')
    return email


class CustomUserCreationForm(UserCreationForm):
    """Registration form. The role is NOT a field: new accounts are always Students."""

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name", "email"):
            self.fields[name].required = True

    def clean_email(self):
        return check_school_email(self.cleaned_data['email'])


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "contact_number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name", "email"):
            self.fields[name].required = True

    def clean_email(self):
        return check_school_email(self.cleaned_data['email'], self.instance.pk)
