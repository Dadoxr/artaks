import unittest
from unittest.mock import patch, MagicMock
from django.db.models.query import QuerySet
from contact.models import Contact
from contact.services.proccess_renew_contacts import download_file,add_or_update_contacts,delete_from_db_if_not_in_new_list,renew_contacts

class TestMyModule(unittest.TestCase):

    def setUp(self):
        self.existing_contacts = Contact.objects.all()
        self.new_contacts = [
            Contact(abc='900', start='7567557', end='546464646', operator='Operator 1', region='Region 1', territory='Territory 1', inn='1234567890'),
            Contact(abc='800', start='4565464', end='909808908', operator='Operator 2', region='Region 2', territory='Territory 2', inn='0987654321')
        ]
    
    @patch('contact.services.proccess_renew_contacts.requests.get')
    def test_download_file(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'Mock file content2'
        mock_requests_get.return_value = mock_response

        download_file('test_file.csv', 'http://example.com/test_file.csv')

        mock_requests_get.assert_called_once_with('http://example.com/test_file.csv', verify=False)

    def test_add_or_update_contacts(self):
        exists_contact_objects_mock = MagicMock(spec=QuerySet)
        exists_contact_objects_mock.filter.return_value = MagicMock(count=MagicMock(return_value=0), exists=MagicMock(return_value=False))

        add_or_update_contacts(exists_contact_objects_mock, [self.new_contacts[0]])

        exists_contact_objects_mock.filter.assert_called()
        exists_contact_objects_mock.filter.return_value.count.assert_called()

    def test_delete_from_db_if_not_in_new_list(self):
        exists_contact_objects_mock = MagicMock(spec=QuerySet)
        exists_contact_objects_mock.exclude.return_value = exists_contact_objects_mock
        exists_contact_objects_mock.exclude.return_value.delete.return_value = None

        delete_from_db_if_not_in_new_list(exists_contact_objects_mock, self.new_contacts)

        expected_exclude_call_args = {
            'abc__in': [contact.abc for contact in self.new_contacts],
            'start__in': [contact.start for contact in self.new_contacts],
            'end__in': [contact.end for contact in self.new_contacts]
        }

        exists_contact_objects_mock.exclude.assert_called_once_with(**expected_exclude_call_args)
        exists_contact_objects_mock.exclude.return_value.delete.assert_called_once()


    @patch('contact.services.proccess_renew_contacts.download_file')
    @patch('contact.services.proccess_renew_contacts.Contact.objects.all')
    @patch('contact.services.proccess_renew_contacts.pd.read_csv')
    def test_renew_contacts(self, mock_read_csv, mock_contact_objects_all, mock_download_file):
        mock_contact_objects_all.return_value = self.existing_contacts

        mock_download_file.return_value = None

        mock_read_csv.return_value = MagicMock(columns=['АВС/ DEF', 'От', 'До', 'Оператор', 'Регион', 'Территория ГАР', 'ИНН'])

        renew_contacts()

        mock_download_file.assert_called()
        mock_contact_objects_all.assert_called()
