import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


class NewBookTest(FunctionalTest):
    def test_add_and_delete_book(self):
        self.browser.get(self.live_server_url)
        self.bookid = None

        # Title
        inputbox = self.browser.find_element_by_id('input-title')
        inputbox.send_keys('Automatically Added Book')

        # Author
        inputbox = self.browser.find_element_by_id('input-author')
        inputbox.send_keys('Robot Author')

        # Submit form
        submitbutton = self.browser.find_element_by_id('book-add')
        submitbutton.click()

        # Wait for page to refresh and check that the table element exists
        if not self.waitfor_table_update('book-table'):
            raise AssertionError('Book table not found')

        # Fetch the table into tuples
        table = self.browser.find_element_by_id('book-table')
        rows = table.find_elements_by_tag_name('tr')

        tds = [row.find_elements_by_tag_name('td') for row in rows]
        rowdata = [(td[0].text, td[1].text, td[2].text) for td in tds if td]

        for i, data in enumerate(rowdata, start=1):
            try:
                self.assertEqual(data[1], 'Automatically Added Book')
                self.assertEqual(data[2], 'Robot Author')

                self.bookid = data[0]
                break
            except AssertionError:
                if i == len(rowdata):
                    raise AssertionError('New book failed to be added')

        if self.bookid:
            deletebutton = self.browser.find_element_by_id(f'book-delete-{self.bookid}')
            deletebutton.click()

        if not self.waitfor_table_update('book-table'):
            raise AssertionError('Page failed to reload after submitting delete request')

        # Fetch the table into tuples
        table = self.browser.find_element_by_id('book-table')
        rows = table.find_elements_by_tag_name('tr')

        tds = [row.find_elements_by_tag_name('td') for row in rows]
        titles = [td[1].text for td in tds if td]

        self.assertNotIn('Automatically Added Book', titles)
