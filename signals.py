# Set up a custom signal
from django.dispatch import Signal#, receiver

invitation_accepted_signal = Signal(providing_args=['invitation', 'user', 'form'])