
from rest_framework import views, response, status

from contact.models import Contact
from contact.services.checking import get_abc_and_body

class ContactAPIiew(views.APIView):
	permission_classes = [True]


	def get(self, request, *args, **kwargs):
		number = request.data.get('owner_pk')
		abc, body = get_abc_and_body(number)
		if abc and body:
			contact_object = Contact.objects.filter(abc=abc, start__lte=body, end__gte=body)
			if contact_object.exists():
				contact = contact_object.first()
				message = 'Номер найден'
				metadata = {
					'operator':contact.operator,
					'region':contact.region,
					'territory':contact.territory,
					'inn':contact.inn,
                }
				status_code = status.HTTP_200_OK
			else:
				message = 'Номер не найден'
				metadata = {}
				status_code = status.HTTP_404_NOT_FOUND
		else:
			message = 'Номер не введен или введен некорректно, попробуйте еще раз (пример 79123456789)'
			metadata = {'nubmer': ''}
			status_code = status.HTTP_400_BAD_REQUEST
		return response.Response({'message':message, 'metadata':metadata}, status=status_code)

