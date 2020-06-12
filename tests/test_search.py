import whoosh
from django.test import TestCase
from unittest.mock import patch, MagicMock, call

from app.search import Search, create_index, remove_index
from tests.settings import INDEX_DIR, TEXT_DIR


class CreateIndexTest(TestCase):

    def tearDown(self):
        try:
            remove_index(INDEX_DIR)
        except ValueError:
            pass

    @patch('whoosh.index.create_in')
    @patch('os.mkdir')
    def test_create_index_calls(self, mkdir, create_in):
        create_index(INDEX_DIR, TEXT_DIR)

        mkdir.assert_called_with(INDEX_DIR)
        calls = [call(id='test_1', text='The scenery scene will continue anyway...'),
                 call(id='test_2', text='...not just to blow observants away.')]
        create_in.return_value.writer().add_document.assert_has_calls(calls, any_order=True)

    def test_create_index_returns_correct_index(self):
        ix = create_index(INDEX_DIR, TEXT_DIR)
        self.assertEqual(ix.storage.folder, INDEX_DIR)
        self.assertListEqual(list(ix._schema._fields.keys()), ['id', 'text'])


class SearchTest(TestCase):

    def setUp(self):
        create_index(INDEX_DIR, TEXT_DIR)

    def tearDown(self):
        try:
            remove_index(INDEX_DIR)
        except ValueError:
            pass

    def test_search_type_default(self):
        search_results = Search(INDEX_DIR, TEXT_DIR).search('blow')
        self.assertEqual(1, len(search_results))
        self.assertEqual('test_2', search_results[0].id)
        self.assertEqual(1, search_results[0].score)
        self.assertEqual(['blow'], search_results[0].matched_terms)
        self.assertEqual('...not just to <strong class="match term0">blow</strong> observants away.', search_results[0].highlights_text)


        


    
