import datetime
from django.urls import reverse, resolve
from django.urls.exceptions import NoReverseMatch
from django.test import TestCase
from cafe.models import User, Permission, Category, Staff, Student
import cafe.urls
from population_script import populate
from cafe.http import HttpResponse

VIEW_NAMES = ["index", "contact", "register", "login", "wait",
        "student_account", "staff_account",
        "view_queries", "thank_you", "staff_thank_you", "logout_screen"]



class BaseTestCase(TestCase):
    """
    Abstract superclass for further tests.
    Populates the database and creates a testAdmin as superuser with acces to
    all views and categories.
    """

    def setUp(self):
        populate(silent=True)
        admin_user = User.objects.create_superuser('testAdmin', 'admin@admin.com', '@dmin123')
        Student.objects.create(user = admin_user)
        Staff.objects.create(user = admin_user)
        for cat in Category.objects.all():
            permission = Permission.objects.get(codename = f"resp-for-{cat.slug}")
            admin_user.user_permissions.add(permission)

class ViewAndTemplateTests(BaseTestCase):
    def setUp(self):
        """
        Log in with superuser to make sure we have full access to the pages.

        Then collect the responses from all the URLs defined in the design spec.
        """
        super().setUp()
        self.client.login(username='testAdmin', password='@dmin123')
        self.response_dict = {}
        for url in VIEW_NAMES:
            try:
                self.response_dict[url] = self.client.get(reverse(url))
            except NoReverseMatch:
                # If a URL is missing, instead of throwing a possibly unhelpful error,
                # we add a placeholder so we can fail a test instead
                self.response_dict[url] = "FAIL"

    def test_views_exist(self):
        for url, response in self.response_dict.items(): 
            with self.subTest():
                # If a name is mapped to a nonexistent template/view
                if response == "FAIL":
                    self.fail(f"VIEW NOT FOUND: {url} defined in spec couldn't be matched to a view.")


    def test_urls_work(self):
        for url, response in self.response_dict.items():
            with self.subTest():
                # If a URL does not load successfully or redirect the user
                if not (response.status_code == 200 or response.status_code == 302):   
                    self.assertEquals(response.status_code, 200, f"PAGE NOT FOUND: {url} defined in spec couldn't be succesfully accessed by superuser.")
    
    def test_pages_link_to_contact_us(self):
        for url, response in self.response_dict.items():
            with self.subTest():
                # Ignore redirects - they lead us to another page that is tested
                if response.status_code != 302:
                    self.assertTrue("Contact Us" in response.content.decode(), f"NO CONTACT US LINK:  {url} contained no link to the Contact Us page for superuser.")
    
    def test_pages_allow_logout(self):
        for url, response in self.response_dict.items():
            with self.subTest():
                # Ignore redirects - they lead us to another page that is tested
                if response.status_code != 302:
                    self.assertTrue("Logout" in response.content.decode(), f"NO LOG OUT LINK: {url} contained no 'Logout' option for superuser.")

    def test_no_undefined_pages(self):
        self.assertTrue(len(VIEW_NAMES) == len(cafe.urls.urlpatterns), f"NON-SPEC VIEW_NAMES FOUND: Found URLs defined in urls.py that were not mentioned in the design spec.")

class StaffViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.logout()
        self.client.login(username = "jsmith", password = "@dmin123")

    def test_staff_has_correct_cats(self):
        # Get all the categories of the test user
        jsmith_cats = [str(i) for i in Staff.objects.get(user = User.objects.get(username = "jsmith")).get_cats_resp()]
        correct_cats = ["General Tutor Feedback", "Test Category"]
        self.assertEqual(jsmith_cats, correct_cats, f"STAFF CATEGORIES WRONG: .get_cats_resp() for 'jsmith' didn't return the correct categories.")

    def test_staff_has_correct_access(self):
        # The main page staff interact with
        response_login = self.client.get(reverse("staff_account"))
        self.assertEqual(response_login.status_code, 200, f"STAFF DENIED ACCESS: Staff couldn't access their login page ({reverse('staff_account')}).")

    def test_staff_sees_correct_issues(self):
        # Make sure staff see all of their categories
        response_login = self.client.get(reverse("staff_account"))
        with self.subTest():
            self.assertTrue("General Tutor Feedback" in response_login.content.decode(), f"CATEGORY NOT FOUND: user 'jsmith' couldn't see the 'General Tutor Feedback' category in '{reverse('staff_account')}'.")
        with self.subTest():
            self.assertTrue("Test Category" in response_login.content.decode(), f"CATEGORY NOT FOUND: user 'jsmith' couldn't see the 'Test Category' category in '{reverse('staff_account')}'.")       

class StudentViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.logout()
        self.client.login(username = "ay", password = "@dmin123")

    def test_student_has_correct_access(self):
        # The query posting view that students are redirected to on login
        response_login = self.client.get(reverse("student_account"))
        # The previous queries view
        response_view_queries = self.client.get(reverse("view_queries"))
        with self.subTest():
            self.assertEqual(response_login.status_code, 200, f"STUDENT DENIED ACCESS: Student couldn't access their login page ({reverse('student_account')}).")
        with self.subTest():
            self.assertEqual(response_view_queries.status_code, 200, f"STUDENT DENIED ACCESS: Student couldn't access their query viewing page ({reverse('view_queries')}).")

    def test_student_sees_correct_issues(self):
        # Make sure students see their own previously posted issues
        response_view_queries = self.client.get(reverse("view_queries"))
        with self.subTest():
            self.assertTrue("Anonymous More Cooper" in response_view_queries.content.decode(), f"ISSUE NOT FOUND: user 'ay' couldn't see the 'Anonymous More Cooper' issue in '{reverse('view_queries')}'.")
        with self.subTest():
            self.assertTrue("Named More Cooper" in response_view_queries.content.decode(), f"ISSUE NOT FOUND: user 'ay' couldn't see the 'Named More Cooper' issue in '{reverse('view_queries')}'.")
        with self.subTest():
            self.assertFalse("Test Issue 1" in response_view_queries.content.decode(), f"WRONG ISSUE FOUND: user 'ay' saw 'Test Issue 1' issue in '{reverse('view_queries')}', even though they shouldn't have access.")

class UnassignedViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.logout()
        # Create a new user that is not yet assigned a student or staff role
        User.objects.create_user('testUser', 'user@user.com', '@dmin123')
        self.client.login(username='testUser', password='@dmin123')
        self.response_dict = {}
        for url in VIEW_NAMES:
            try:
                self.response_dict[url] = self.client.get(reverse(url))
            except NoReverseMatch:
                self.response_dict[url] = "FAIL"
    
    def test_unassigned_redirects(self):
        # Make sure the unassigned user is redirected from pages that do redirect
        for url, response in self.response_dict.items():
            with self.subTest():
                if not (url == "login" or url == "logout_screen" or url == "register"
                        or url == "wait" or url == "index" or url == "contact" or
                        response.status_code == 302):
                    self.fail(f"UNASSIGNED USER ACCESS: Unassigned user was not redirected from {url} to an appropriate page.")