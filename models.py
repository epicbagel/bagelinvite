import datetime
import random

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _

__all__ = ['Invitation']

class InvitationManager(models.Manager):
	
	def create_invitation(self, to_user):
		"""
		Create an ``Invitation`` and returns it.
		
		The code for the ``Invitation`` will be a SHA1 hash, generated
		from a combination of the ``User``'s username and a random salt.
		"""
		kwargs = {'to_user': to_user}
		
		date_invited = datetime.datetime.now()
		
		kwargs['date_invited'] = date_invited
		
		kwargs['expiration_date'] = date_invited + datetime.timedelta(getattr(settings, 'ACCOUNT_INVITATION_DAYS', 30))
		
		salt = sha_constructor(str(random.random())).hexdigest()[:5]
		
		kwargs['code'] = sha_constructor("%s%s%s" % (datetime.datetime.now(), salt, to_user.username)).hexdigest()
		
		return self.create(**kwargs)

	def delete_expired_invitations(self):
		"""
		Deletes all unused ``Invitation`` objects that are past the expiration date
		"""
		self.filter(expiration_date__lt=datetime.datetime.now(), used=False).delete()


class Invitation(models.Model):
	
	code = models.CharField(_('invitation code'), max_length = 40)
	
	date_invited = models.DateTimeField()
	
	expiration_date = models.DateTimeField()
	
	used = models.BooleanField(default = False)
	
	to_user = models.ForeignKey(User)
	
	from_user = models.ForeignKey(User, related_name = 'from_user')

	objects = InvitationManager()

	def __unicode__(self):
		
		return u"Invitation to %s" % self.to_user

	def expired(self):
		
		return self.expiration_date < datetime.datetime.now()

	def send(self, from_email = settings.DEFAULT_FROM_EMAIL):

		current_site = Site.objects.get_current()

		subject = render_to_string('invitation/invitation_email_subject.txt', {
		
			'invitation': self,
		
			'site': current_site,
									
		})
									
		# Email subject *must not* contain newlines
		subject = ''.join(subject.splitlines())

		message = render_to_string('invitation/invitation_email.txt', {
		
			'invitation': self,
			
			'expiration_days': getattr(settings, 'ACCOUNT_INVITATION_DAYS', 30),
			
			'site': current_site,
			
			'from_user' : self.from_user,
			
		})

		send_mail(subject, message, from_email, [self.to_user.email])



# Returns whether or not a user has invitations associated with it
User.has_invitation = property(lambda user: Invitation.objects.filter(to_user = user, used = False).count() > 0)