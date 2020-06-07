from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import unittest


class FunctionalTest(unittest.TestCase):

    def setUp(self):
        
        options = Options()
        options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        
        self.browser = webdriver.Chrome(chrome_options=options)

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_query_and_see_results(self):

        # Dao is researching the Pali Canons and wants to find a phrase
        # He fires up the search page
        self.browser.get('http://localhost:8000')

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

        # When he hits enter, the page updates and 
        # the search results are displayed
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        table = self.browser.find_element_by_id('id_search_results')
        rows = table.find_elements_by_tag_name('tr')
        self.assertTrue(any(row.text == 'chokname rypone' for row in rows))