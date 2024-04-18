import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from contact.models import Contact
from contact.services.proccess_renew_contacts import download_file, add_or_update_contacts, delete_from_db_if_not_in_new_list, renew_contacts

class TestMyModule(unittest.TestCase):

    def setUp(self):
        self.existing_contacts = [
            {
                '1234567': Contact(abc='123', start='456', end='789', operator='Operator 1', region='Region 1', territory='Territory 1', inn='1234567890')
            },
            {
                '4567890': Contact(abc='456', start='789', end='012', operator='Operator 2', region='Region 2', territory='Territory 2', inn='0987654321')
            }
        ]
        self.new_contacts = [
            {
                '9007567557546464646': {'abc': '900', 'start': '7567557', 'end': '546464646', 'operator': 'Operator 1', 'region': 'Region 1', 'territory': 'Territory 1', 'inn': '1234567890'}
            },
            {
                '8004565464909808908': {'abc': '800', 'start': '4565464', 'end': '909808908', 'operator': 'Operator 2', 'region': 'Region 2', 'territory': 'Territory 2', 'inn': '0987654321'}
            }
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
        exists_contact_objects_mock = self.existing_contacts
        add_or_update_contacts(exists_contact_objects_mock, [self.new_contacts[0]])

        exists_contact_obj = next(iter(self.existing_contacts[0].values()))
        self.assertEqual(exists_contact_obj.operator, 'Operator 1')


    @patch('contact.services.proccess_renew_contacts.download_file')
    @patch('contact.services.proccess_renew_contacts.Contact.objects.all')
    @patch('contact.services.proccess_renew_contacts.pd.read_csv')
    def test_renew_contacts(self, mock_read_csv, mock_contact_objects_all, mock_download_file):
        mock_contact_objects_all.return_value = self.existing_contacts
        mock_download_file.return_value = None
        mock_read_csv.return_value = pd.DataFrame({
            'АВС/ DEF': ['900', '800'],
            'От': ['7567557', '4565464'],
            'До': ['546464646', '909808908'],
            'Оператор': ['Operator 1', 'Operator 2'],
            'Регион': ['Region 1', 'Region 2'],
            'Территория ГАР': ['Territory 1', 'Territory 2'],
            'ИНН': ['1234567890', '0987654321']
        })

        renew_contacts()

        self.assertTrue(mock_download_file.called)
        self.assertTrue(mock_contact_objects_all.called)
