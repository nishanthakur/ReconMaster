from django import forms
from .models import Domain
from reconMaster.validators import validate_domain


class AddTargetForm(forms.Form):
    domain_name = forms.CharField(
        validators=[validate_domain],
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "domainName",
                "placeholder": "domain.com"
            }
        ))
    domain_description = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "domainDescription",
                "placeholder": "optional"
            }
        ))