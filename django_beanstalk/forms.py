from django import forms
from django.forms.widgets import Textarea

class BeanstalkJobForm(forms.Form):
    body = forms.CharField(widget=Textarea, max_length=65535, required=True) # or 2^16 see protocol.txt (beanstalkd)
