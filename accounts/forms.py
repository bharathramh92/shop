from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist

from accounts.models import Address

login_wrong_username_password = "username/password combination was incorrect"
registration_same_email_address = "User exists with same email id. Use different email address"
registration_passwords_not_matching = "Passwords are not matching"
email_not_found = "Given email address not found in our database. Please check again and enter the email address."
wrong_current_password = "Current password is wrong."
login_username_password_null = "Please enter username/password"


class LoginForm(forms.Form):

    username = forms.CharField(label='Username/Email',
                               max_length=100,
                               required=True)

    loginPassword = forms.CharField(widget=forms.PasswordInput,
                                    label='Password',
                                    max_length=20,
                                    required=True)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('username')
        login_password = cleaned_data.get('loginPassword')

        if username is None or login_password is None:
            raise forms.ValidationError(login_username_password_null, code='invalid')

        if '@' in username:
            try:
                username = User.objects.get(email=username).username
            except ObjectDoesNotExist:
                raise forms.ValidationError(login_wrong_username_password, code='invalid')

        user = authenticate(username=username, password=login_password)
        if user is None:
            self.add_error('loginPassword', login_wrong_username_password)
        self.cleaned_data['user'] = user


def does_email_exists(email):
    try:
        # in case more than one user got created accidentally with same email earlier
        if len(User.objects.filter(email=email)) == 0:
            return False
        raise Exception
    except Exception as e:
        return True


class RegisterForm(forms.Form):

    email = forms.EmailField(label='Email',
                             max_length=100,
                             required=True)

    firstName = forms.CharField(label='First Name',
                                max_length=30,
                                required=True,
                                min_length=2)

    lastName = forms.CharField(label='Last Name',
                               max_length=30,
                               required=True,
                               min_length=2)

    password = forms.CharField(widget=forms.PasswordInput,
                               label='Password',
                               max_length=20,
                               required=True)

    confirmPassword = forms.CharField(widget=forms.PasswordInput,
                                      label='Confirm Password',
                                      max_length=20,
                                      required=True)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirmPassword')

        if does_email_exists(email):
            self.add_error('email', registration_same_email_address)

        if password != confirm_password:
            self.add_error('password', registration_passwords_not_matching)


class EmailForm(forms.Form):

    email = forms.EmailField(label='Email',
                             max_length=100,
                             required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except Exception:
            self.add_error('email', email_not_found)
        return email


class ForgotPasswordForm(forms.Form):

    password = forms.CharField(widget=forms.PasswordInput,
                               label='Password',
                               max_length=20,
                               required=True)

    confirmPassword = forms.CharField(widget=forms.PasswordInput,
                                      label='Confirm Password',
                                      max_length=20,
                                      required=True)

    def clean(self):
        cleaned_data = super(ForgotPasswordForm, self).clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirmPassword')

        if password != confirm_password:
            self.add_error('password', registration_passwords_not_matching)


class ChangePasswordForm(forms.Form):

    currentPassword = forms.CharField(widget=forms.PasswordInput,
                                      label='Current Password',
                                      max_length=20,
                                      required=True)

    newPassword = forms.CharField(widget=forms.PasswordInput,
                                  label='New Password',
                                  max_length=20,
                                  required=True)

    confirmNewPassword = forms.CharField(widget=forms.PasswordInput,
                                         label='Confirm New Password',
                                         max_length=20,
                                         required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        current_password = cleaned_data.get('currentPassword')
        new_password = cleaned_data.get('newPassword')
        confirm_new_password = cleaned_data.get('confirmNewPassword')

        if not self.user.check_password(current_password):
            self.add_error('currentPassword', wrong_current_password)

        if new_password != confirm_new_password:
            self.add_error('newPassword', registration_passwords_not_matching)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user', 'last_updated_datetime', 'added_datetime']


class AccountForm(forms.Form):

    firstName = forms.CharField(label='First Name',
                                max_length=30,
                                required=True)

    lastName = forms.CharField(label='First Name',
                               max_length=30,
                               required=True)

    countryCodePhoneNumber = forms.CharField(label='Phone number country code',
                                             max_length=5,
                                             required=False)

    phoneNumber = forms.CharField(widget=forms.NumberInput,
                                  label='Phone number',
                                  max_length=15,
                                  required=False)
