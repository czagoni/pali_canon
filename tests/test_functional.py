from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import unittest


class FunctionalTest(unittest.TestCase):

    def setUp(self):
        
        options = Options()
        options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        
        self.browser = webdriver.Chrome(chrome_options=options)

    def tearDown(self):
        self.browser.quit()

    def test_index_page_can_be_opened(self):

        self.browser.get('http://localhost:8000')

        self.assertIn('Buddha', self.browser.title)
        self.fail('Finish the test')
