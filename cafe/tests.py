import datetime
from django.urls import reverse, resolve
from django.urls.exceptions import NoReverseMatch
from django.test import TestCase
from cafe.models import User, Staff
import cafe.urls
from populate_db import populate

VIEW_NAMES = ["index", "contact", "register", "login", "wait",
        "student_account", "staff_account",
        "view_queries"]



class BaseTestCase(TestCase):
    """
    Abstract superclass for further tests.
    Populates the database and creates a testAdmin as superuser.
    """

    def setUp(self):
        populate()
        User.objects.create_superuser('testAdmin', 'admin@admin.com', '@dmin123')

class ViewAndTemplateTests(BaseTestCase):
    def setUp(self):
        """
        Log in with superuser to make sure we have full access to the pages.

        Then collect the responses from all the URLs defined in the design spec.
        """
        self.client.login(username='testAdmin', password='@dmin123')
        self.response_dict = {}

    def test_views_exist(self):
        for url in VIEW_NAMES:
            try:
                self.response_dict[url] = self.client.get(reverse(url))
            except NoReverseMatch:
                self.fail(f"VIEW NOT FOUND: {url} defined in spec couldn't be matched to a view.")


    def test_urls_work(self):
        for url, response in self.response_dict.items():
            self.assertEquals(response.status_code, 200, f"PAGE NOT FOUND: {url} defined in spec couldn't be succesfully accessed by superuser.")
    
    def test_pages_link_to_contact_us(self):
        for url, response in self.response_dict.items():
            self.assertTrue(reverse("contact_us") in response.content.decode(), f"NO CONTACT US LINK:  {url} contained no link to the Contact Us page for superuser.")
    
    def test_pages_allow_logout(self):
        for url, response in self.response_dict.items():
            self.assertTrue("Log Out" in response.content.decode(), f"NO LOG OUT LINK: {url} contained no 'Log Out' option for superuser.")

    def test_no_undefined_pages(self):
        self.assertTrue(len(VIEW_NAMES) == len(cafe.urls.urlpatterns), f"NON-SPEC VIEW_NAMES FOUND: Found URLs defined in urls.py that were not mentioned in the design spec.")

class StaffViewTests(BaseTestCase):
    def setUp(self):
        self.client.logout()
        self.client.login(username = "jsmith", password = "@dmin123")

    def test_staff_has_correct_cats(self):
        jsmith_cats = [str(i) for i in Staff.objects.get(user = User.objects.get(username = "jsmith").get_cats_resp())]
        jsmith_cats.sort()
        correct_cats = ["General Tutor Feedback", "Test Category"]
        self.assertEqual(jsmith_cats, correct_cats, f"STAFF CATEGORIES WRONG: .get_cats_resp() for 'jsmith' didn't return the correct categories.")

    def test_staff_has_correct_access(self):
        response_login = self.client.get(reverse("staff_account"))
        response_response_creation = self.client.get(reverse("create_response"))
        self.assertEqual(response_login.status_code, 200, f"STAFF DENIED ACCESS: Staff couldn't access their login page ({reverse('staff_account')}).")
        self.assertEqual(response_response_creation.status_code, 200, f"STAFF DENIED ACCESS: Staff couldn't access their response writing page ({reverse('create_response')}).")

    def test_staff_sees_correct_issues(self):
        response_login = self.client.get(reverse("staff_account"))
        self.assertTrue("General Tutor Feedback" in response_login.content.decode(), f"CATEGORY NOT FOUND: user 'jsmith' couldn't see the 'General Tutor Feedback' category in '{reverse('staff_account')}'.")
        self.assertTrue("Test Category" in response_login.content.decode(), f"CATEGORY NOT FOUND: user 'jsmith' couldn't see the 'Test Category' category in '{reverse('staff_account')}'.")
        self.assertFalse("CS1P Feedback" in response_login.content.decode(), f"WRONG CATEGORY FOUND: user 'jsmith' saw 'CS1P Feedback' category in '{reverse('staff_account')}', even though they shouldn't have access.")
        self.assertFalse("Online Learning Feedback" in response_login.content.decode(), f"WRONG CATEGORY FOUND: user 'jsmith' saw 'Online Learning Feedback' category in '{reverse('staff_account')}', even though they shouldn't have access.")        

class StudentViewTests(BaseTestCase):
    def setUp(self):
        self.client.logout()
        self.client.login(username = "ay", password = "@dmin123")

    def test_student_has_correct_access(self):
        response_login = self.client.get(reverse("student_account"))
        response_view_queries = self.client.get(reverse("view_queries"))
        self.assertEqual(response_login.status_code, 200, f"STAFF DENIED ACCESS: Student couldn't access their login page ({reverse('student_account')}).")
        self.assertEqual(response_view_queries.status_code, 200, f"STAFF DENIED ACCESS: Student couldn't access their query viewing page ({reverse('view_queries')}).")

    def test_student_sees_correct_issues(self):
        response_view_queries = self.client.get(reverse("view_queries"))
        self.assertTrue("Anonymous More Cooper" in response_view_queries.content.decode(), f"ISSUE NOT FOUND: user 'ay' couldn't see the 'Anonymous More Cooper' issue in '{reverse('view_queries')}'.")
        self.assertTrue("Named More Cooper" in response_view_queries.content.decode(), f"ISSUE NOT FOUND: user 'ay' couldn't see the 'Named More Cooper' issue in '{reverse('view_queries')}'.")
        self.assertFalse("Test Issue 1" in response_view_queries.content.decode(), f"WRONG ISSUE FOUND: user 'ay' saw 'Test Issue 1' issue in '{reverse('view_queries')}', even though they shouldn't have access.")
