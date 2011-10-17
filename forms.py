from django import forms
from django.utils.translation import ugettext_lazy as _

class Invitation_Form(forms.Form):

	password = forms.CharField(label = _('Create a password'), widget = forms.PasswordInput(render_value=True))