from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException 
import time
import unittest
from django.test import LiveServerTestCase


class FunctionalTest(LiveServerTestCase):

    MAX_WAIT = 10

    def setUp(self):
        
        options = Options()
        options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        
        self.browser = webdriver.Chrome(options=options)

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_query_and_see_results(self):

        # Dao is researching the Pali Canons and wants to find a phrase
        # He fires up the search page
        self.browser.get(self.live_server_url)

        # The page title and the header tell him what this is all about
        self.assertIn('Pali Canon Search', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Pali Canon Search', header_text)

        # He notices the search query box
        inputbox = self.browser.find_element_by_id('id_search_query_box')
        self.assertEqual(inputbox.get_attribute('placeholder'),
                         'Enter a search query')

        # He types "choknam rypone" in the text box
        inputbox.send_keys("choknam rypone")

        # When he hits enter,
        # the search results are displayed
        inputbox.send_keys(Keys.ENTER)

        # The page title and the header tell him what this is all about
        self.assertIn('Pali Canon Search Results', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Pali Canon Search Results', header_text)
        self.wait_for_row_in_list_table('choknam rypone')

    def wait_for_row_in_list_table(self, row_text): 

        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('id_search_results') 
                rows = table.find_elements_by_tag_name('tr') 
                self.assertIn(row_text, [row.text for row in rows]) 
                return
            except (AssertionError, WebDriverException) as e: 
                if time.time() - start_time > self.MAX_WAIT:
                    raise e 
                time.sleep(0.5)