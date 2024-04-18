import logging
from django import forms
from contact.services.checking import get_abc_and_body

logger = logging.getLogger(__name__)

class ContactForm(forms.Form):
    number = forms.IntegerField(label='номер в формате 79123456789', required=True)

    def format_number(self, request):
        number = str(self.cleaned_data['number'])
        
        abc, body = get_abc_and_body(number)
        
        return abc, body

        
