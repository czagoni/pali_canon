from django.test import TestCase
from unittest.mock import patch, MagicMock, call

from app.search import Search
import whoosh


class SearchTest(TestCase):

    def setUp(self):
        self.index_dir = './tests/index_dir'
        self.text_dir = './tests/test_texts'

    @patch('whoosh.index.open_dir')
    def test_existing_index(self, open_dir):
        open_dir.return_value = 'Index'
        search = Search(index_dir=self.index_dir, text_dir=self.text_dir)

        open_dir.assert_called_with(self.index_dir)
        self.assertEqual('Index', search.ix)

    @patch('whoosh.index.create_in')
    @patch('os.mkdir')
    def test_create_index(self, mkdir, create_in):
        Search(index_dir=self.index_dir, text_dir=self.text_dir)

        mkdir.assert_called_with(self.index_dir)
        calls = [call(id='test_1', text='The scenery scene will continue anyway...'),
                 call(id='test_2', text='...not just to blow observants away.')]
        create_in.return_value.writer().add_document.assert_has_calls(calls, any_order=True)
