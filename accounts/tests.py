from django.test import TestCase
from django.urls import reverse

from .models import CustomUser

PASSWORD = 'S3cure-Pass!9'
VALID = {
    'username': 'juan', 'first_name': 'Juan', 'last_name': 'Dela Cruz',
    'email': 'juan@cit.edu', 'password1': PASSWORD, 'password2': PASSWORD,
}


def make_student(username='maria', email='maria@cit.edu'):
    return CustomUser.objects.create_user(username=username, email=email, password=PASSWORD,
                                          first_name='Maria', last_name='Santos')


def make_admin(username='boss', email='boss@cit.edu'):
    return CustomUser.objects.create_superuser(username=username, email=email, password=PASSWORD)


class RegistrationTests(TestCase):
    def post(self, **changes):
        return self.client.post(reverse('accounts:signup'), {**VALID, **changes})

    def test_valid_registration_creates_student_with_hashed_password(self):
        r = self.post()
        self.assertRedirects(r, reverse('accounts:login'))
        user = CustomUser.objects.get(username='juan')
        self.assertEqual(user.role, CustomUser.Role.STUDENT)
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))

    def test_success_message_is_shown(self):
        r = self.client.post(reverse('accounts:signup'), VALID, follow=True)
        self.assertContains(r, 'Account created successfully')

    def test_cannot_register_as_admin(self):
        self.post(role='ADMIN')
        self.assertEqual(CustomUser.objects.get(username='juan').role, CustomUser.Role.STUDENT)

    def test_required_fields(self):
        r = self.client.post(reverse('accounts:signup'), {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(CustomUser.objects.count(), 0)
        self.assertContains(r, 'This field is required')

    def test_invalid_email_format(self):
        self.assertEqual(self.post(email='not-an-email').status_code, 200)
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_non_school_email_rejected(self):
        r = self.post(email='juan@gmail.com')
        self.assertContains(r, 'school email')
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_duplicate_username_rejected(self):
        make_student(username='juan', email='other@cit.edu')
        self.assertContains(self.post(), 'already exists')
        self.assertEqual(CustomUser.objects.count(), 1)

    def test_duplicate_email_rejected_case_insensitive(self):
        make_student(username='maria', email='juan@cit.edu')
        self.assertContains(self.post(email='JUAN@cit.edu'), 'already exists')
        self.assertEqual(CustomUser.objects.count(), 1)

    def test_password_confirmation_must_match(self):
        r = self.post(password2='Different-Pass!1')
        self.assertContains(r, "didn")  # "The two password fields didn't match."
        self.assertEqual(CustomUser.objects.count(), 0)


class LoginLogoutTests(TestCase):
    def test_valid_login_goes_to_student_dashboard(self):
        make_student()
        r = self.client.post(reverse('accounts:login'), {'username': 'maria', 'password': PASSWORD})
        self.assertRedirects(r, reverse('dashboard:home'), fetch_redirect_response=False)
        r = self.client.get(reverse('dashboard:home'), follow=True)
        self.assertEqual(r.redirect_chain[-1][0], reverse('dashboard:student_home'))

    def test_invalid_login_shows_error(self):
        make_student()
        r = self.client.post(reverse('accounts:login'), {'username': 'maria', 'password': 'wrong'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Please enter a correct username and password')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_ends_session(self):
        make_student()
        self.client.login(username='maria', password=PASSWORD)
        r = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(r, reverse('accounts:login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_protected_pages_redirect_to_login(self):
        for name in ('dashboard:home', 'dashboard:student_home', 'dashboard:admin_panel',
                     'accounts:profile', 'accounts:profile_edit'):
            url = reverse(name)
            r = self.client.get(url)
            self.assertRedirects(r, f"{reverse('accounts:login')}?next={url}", fetch_redirect_response=False)


class RoleDashboardTests(TestCase):
    def test_admin_login_lands_on_admin_panel(self):
        make_admin()
        self.client.login(username='boss', password=PASSWORD)
        r = self.client.get(reverse('dashboard:home'))
        self.assertRedirects(r, reverse('dashboard:admin_panel'), fetch_redirect_response=False)
        self.assertContains(self.client.get(reverse('dashboard:admin_panel')), 'Administrator dashboard')

    def test_superuser_gets_admin_role(self):
        self.assertEqual(make_admin().role, CustomUser.Role.ADMIN)

    def test_student_cannot_open_admin_panel(self):
        make_student()
        self.client.login(username='maria', password=PASSWORD)
        r = self.client.get(reverse('dashboard:admin_panel'))
        self.assertRedirects(r, reverse('dashboard:home'), fetch_redirect_response=False)
        r = self.client.get(reverse('dashboard:admin_panel'), follow=True)
        self.assertContains(r, 'You do not have access')
        self.assertNotContains(r, 'Administrator dashboard')

    def test_admin_cannot_open_student_dashboard(self):
        make_admin()
        self.client.login(username='boss', password=PASSWORD)
        r = self.client.get(reverse('dashboard:student_home'))
        self.assertRedirects(r, reverse('dashboard:home'), fetch_redirect_response=False)

    def test_student_cannot_open_django_admin_site(self):
        make_student()
        self.client.login(username='maria', password=PASSWORD)
        r = self.client.get('/admin/')
        self.assertEqual(r.status_code, 302)


class ProfileTests(TestCase):
    def setUp(self):
        self.user = make_student()
        self.client.login(username='maria', password=PASSWORD)

    def test_view_profile(self):
        self.assertContains(self.client.get(reverse('accounts:profile')), 'maria@cit.edu')

    def test_update_profile(self):
        r = self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Maria', 'last_name': 'Reyes', 'email': 'maria.reyes@cit.edu',
            'contact_number': '09171234567'})
        self.assertRedirects(r, reverse('accounts:profile'))
        self.user.refresh_from_db()
        self.assertEqual((self.user.last_name, self.user.email, self.user.contact_number),
                         ('Reyes', 'maria.reyes@cit.edu', '09171234567'))

    def test_cannot_change_role_through_profile(self):
        self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Maria', 'last_name': 'Santos', 'email': 'maria@cit.edu', 'role': 'ADMIN'})
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, CustomUser.Role.STUDENT)

    def test_cannot_take_another_users_email(self):
        make_student('pedro', 'pedro@cit.edu')
        r = self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Maria', 'last_name': 'Santos', 'email': 'pedro@cit.edu'})
        self.assertContains(r, 'already exists')

    def test_user_only_edits_own_profile(self):
        other = make_student('pedro', 'pedro@cit.edu')
        self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Hacked', 'last_name': 'Name', 'email': 'maria@cit.edu'})
        other.refresh_from_db()
        self.assertEqual(other.first_name, 'Maria')  # make_student default; Pedro untouched
