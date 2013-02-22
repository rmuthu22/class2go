from django.test import LiveServerTestCase
from nose.plugins.attrib import attr
from selenium import webdriver
try:
    from pyvirtualdisplay import Display    # Make virtual display ability optional
except ImportError, msg:
    Display = False
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0

from os import environ
import sys

def debug_out(s):
    pass
def debug_out_working(s):
    sys.stderr.write(s)
debug_out = debug_out_working

@attr('slow')
class SeleniumTestBase(LiveServerTestCase):

    @classmethod
    def setup_class(cls):
        headless = environ.get('C2G_HEADLESS_TESTS', 0)
        webdriver_preference = environ.get('C2G_SELENIUM_WEBDRIVER', 'chrome')
        if headless:
            if Display:
                cls.display = Display(visible=0, size=(800, 600))
                cls.display.start()
            # Ok, asked for headless but we can't support it - so run with a head 
            print "WARNING: C2G_HEADLESS_TESTS specified, but pyvirtualdisplay not installed."
            print "         Continuing assuming native X display available."
        if webdriver_preference == 'chrome':
            cls.browser = webdriver.Chrome()
        elif webdriver_preference == 'firefox':
            cls.browser = webdriver.Firefox()
        super(SeleniumTestBase, cls).setUpClass()

    @classmethod
    def teardown_class(cls):
        cls.browser.quit()
        if Display:
            cls.display.stop()
        super(SeleniumTestBase, cls).tearDownClass()

    def do_login(self):
        """Login with the preset username & password"""
        browser = self.browser
        debug_out("DEBUG: got browser\n")
        # fetch the page and make sure it loads and we have a user entry field
        browser.get('%s%s' % (self.live_server_url, self.login_path))

        debug_out("DEBUG: got live_server_url %s\n" % self.live_server_url)

        WebDriverWait(browser, 10).until(lambda browser : browser.find_element_by_id('id_username'))

        debug_out("DEBUG: got username box\n")
        # now that we have the page, fill out the form
        userField = browser.find_element_by_id('id_username')
        userField.send_keys(self.username)
        passField = browser.find_element_by_id('id_password')
        passField.send_keys(self.password)

        # trigger the form submission
        inputEle = browser.find_element_by_xpath('//input[@type="submit"]')
        inputEle.submit()

        # wait at most 10 seconds or until we see evidence of login
        WebDriverWait(browser, 10).until(lambda browser : browser.find_element_by_xpath('//span[contains(text(), "Welcome")]'))
        debug_out("DEBUG: looks like we're logged in as %s\n" % self.username)

class StudentBase(SeleniumTestBase):
    """
    A class that defines the configurable data needed to target a specific
    course for a specific user.
    """
    fixtures = ['db_snapshot_video_tests.json']
    login_path = '/accounts/login'
    course_prefix = 'networking'
    course_suffix = 'Fall2012'
    course_name = 'Natural Language Processing'
    username = 'student_1'
    user_type = 'student'
    password = 'class2go'

class InstructorBase(SeleniumTestBase):
    """
    A class that defines the configurable data needed to target a specific
    course for a specific user.
    """
    fixtures = ['db_snapshot_video_tests.json']
    login_path = '/accounts/login'
    course_prefix = 'networking'
    course_suffix = 'Fall2012'
    course_name = 'Natural Language Processing'
    username = 'professor_0'
    user_type = 'instructor'
    password = 'class2go'


