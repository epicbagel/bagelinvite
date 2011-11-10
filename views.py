import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from django.utils.importlib import import_module


from signals import invitation_accepted_signal
from models import Invitation

def get_form():

	try:

		path = getattr(settings, 'INVITATION_FORM', 'bagelinvite.forms.Invitation_Form')

		mod_name, klass_name = path.rsplit('.', 1)
	
		mod = import_module(mod_name)
	
	except ImportError, e:

		raise ImproperlyConfigured(('Error importing email backend module %s: "%s"' % (mod_name, e)))
	
	try:

		return getattr(mod, klass_name)
	
	except AttributeError:

		raise ImproperlyConfigured(('Module "%s" does not define a ''"%s" class' % (mod_name, klass_name)))

@transaction.commit_on_success
def invitation_accepted(request, invitation_code, success_url = settings.LOGIN_REDIRECT_URL, template_name = 'invitation/accepted.html'):	
	
	form_class = get_form()
	
	error_msg = None
	
	try:
		invitation = Invitation.objects.get(code=invitation_code)
		
		if invitation.expired():
			
			error_msg = _("This invitation has expired.")
			
	except Invitation.DoesNotExist:
		
		error_msg = _("The invitation code is not valid. Please check the link provided and try again.")

	if error_msg is not None:

		context = {'error_msg': error_msg}

		context.update(csrf(request))

		return direct_to_template(request, 'invitation/invalid.html', context)

	if request.method == 'POST':

		form = form_class(request.POST)

		if form.is_valid():
			
			to_user = invitation.to_user
	
			# Send signal for new invitation
			invitation_accepted_signal.send_robust(sender = None, invitation = invitation, user = to_user, form = form)

			# Set the password
			password = form.cleaned_data['password']

			to_user.set_password(password)

			to_user.save()

			# Delete the invitation now they've signed up
			invitation.delete()

			user = authenticate(username = invitation.to_user.username, password = password)

			login(request, user)
			
			try:
			
				return HttpResponseRedirect(user.get_profile().get_absolute_url())
	
			except AttributeError:
	
				# Redirect the user to their new account page
				return HttpResponseRedirect('/')

	else:
		
		form = form_class()
		
	return direct_to_template(request, template_name, {
	
		'site' : Site.objects.get_current(),
	
		'form': form,
		
		'invitation': invitation,
		
	})

