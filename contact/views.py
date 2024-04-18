from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages

from contact.forms import ContactForm
from contact.models import Contact


class ContactFormView(generic.FormView):
    template_name = 'contact/main.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:main')

    def form_valid(self, form):
        abc, body = form.format_number(self.request)

        if abc and body:

            contact_object = Contact.objects.filter(abc=abc, start__lte=body, end__gte=body)
            if contact_object.exists():
                messages.info(self.request, contact_object.first())
            else:
                messages.info(self.request, 'Номер не найден')
        else:
            messages.error(self.request, 'Номер введен некорректно, попробуйте еще раз')
        response = super().form_invalid(form)
        return response
