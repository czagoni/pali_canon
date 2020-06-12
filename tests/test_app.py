from django.urls import resolve
from django.test import TestCase
from django.http import HttpRequest

from app.views import home_page
from app.search import SearchResult


class HomePageTest(TestCase):

    def test_home_page_returns_correct_html(self):

        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_search_query_post_request(self):

        search_result = SearchResult(id='id', score=1, matched_terms=['term_1', 'term_2'], 
                                     highlights_text='text <strong class="match term0">term_1</strong> text')
        response = self.client.post('/results/', data={'search_results': search_result}) 
        self.assertIn('Number of matches in text id: 1', response.content.decode()) 
        self.assertTemplateUsed(response, 'results.html')
