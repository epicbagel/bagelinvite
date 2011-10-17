from django.contrib import admin
from models import Invitation

class InvitationAdmin(admin.ModelAdmin):
	
	list_display = ('__unicode__', 'to_user', 'date_invited', 'used', 'invitation_expired')

	def invitation_expired(self, obj):
	
		return obj.expired()

	invitation_expired.boolean = True

admin.site.register(Invitation, InvitationAdmin)
