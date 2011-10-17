from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from views import invitation_accepted

urlpatterns = patterns('',

	url(r'^invite/complete/$', direct_to_template, {'template': 'invitation/invitation_complete.html'}, name='invitation_complete'),

	url(r'^invite/(?P<invitation_code>\w+)/$', invitation_accepted, name='invitation_accepted'),

)
