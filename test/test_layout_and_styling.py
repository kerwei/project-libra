from .base import FunctionalTest
from selenium.webdriver.common.keys import Keys


class LayoutAndStylingTest(FunctionalTest):
    def test_layout_and_styling(self):
        # Homepage
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # Form elements
        inputbox = self.browser.find_element_by_id('input-title')
        self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width']/2, 240, delta=15)

        inputbox = self.browser.find_element_by_id('input-author')
        self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width']/2, 240, delta=15)