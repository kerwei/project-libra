from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from unittest import skip

import os
import time
import unittest
import pdb

MAXWAIT = 10


class FunctionalTest(unittest.TestCase):
    def setUp(self):
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('browser.cache.disk.enable', False)
        self.profile.set_preference('browser.cache.memory.enable', False)
        self.profile.set_preference('browser.cache.offline.enable', False)
        self.profile.set_preference('network.http.use-cache', False)

        self.browser = webdriver.Firefox(self.profile)
        # self.live_server_url = 'http://54.179.151.212:5000/'
        self.live_server_url = 'http://localhost:5000/'

    def tearDown(self):
        self.browser.quit()

    def waitfor_table_update(self, tblid):
        starttime = time.time()

        while True:
            try:
                self.browser.find_element_by_id(tblid)
                return True
            except (AssertionError, WebDriverException):
                if time.time() - starttime > MAXWAIT:
                    return False
                time.sleep(0.5)