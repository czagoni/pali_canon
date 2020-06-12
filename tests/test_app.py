from django.urls import resolve
from django.test import TestCase, override_settings
from django.http import HttpRequest

from app.views import home_page
from app.search import Search, create_index, remove_index
from tests.settings import INDEX_DIR, TEXT_DIR


@override_settings(INDEX_DIR=INDEX_DIR)
@override_settings(TEXT_DIR=TEXT_DIR)
class HomePageTest(TestCase):

    def setUp(self):
        create_index(INDEX_DIR, TEXT_DIR)

    def tearDown(self):
        try:
            remove_index(INDEX_DIR)
        except ValueError:
            pass

    def test_home_page_returns_correct_html(self):

        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_search_query_post_request(self):

        response = self.client.post('/results/', data={'search_query_text': 'blow'}) 
        self.assertIn('Number of matches in text test_2: 1', response.content.decode()) 
        self.assertTemplateUsed(response, 'results.html')

    def test_search_query_post_request_no_results(self):

        response = self.client.post('/results/', data={'search_query_text': 'crow'}) 
        self.assertIn('No results', response.content.decode()) 
        self.assertTemplateUsed(response, 'results.html')
