from django.urls import resolve
from django.test import TestCase
from django.http import HttpRequest

from app.views import home_page


class HomePageTest(TestCase):

    def test_home_page_returns_correct_html(self): 

        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_search_query_post_request(self):
        response = self.client.post('/', data={'search_query_text': 'Search Query'}) 
        self.assertIn('Search Query', response.content.decode()) 
        self.assertTemplateUsed(response, 'home.html')