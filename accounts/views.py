import random
import datetime

from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from accounts.models import User, UserExtended, EmailVerification, ForgotPasswordVerification, Address
from shop import settings_sensitive
from accounts.forms import RegisterForm, LoginForm, ForgotPasswordForm, EmailForm, AddressForm, ChangePasswordForm
from accounts.forms import AccountForm

login_wrong_username_password = "username/password combination was incorrect"
registration_email_verification = "Please click the following link to verify your account"
forgot_password_message = "Please click the following link to reset your password"
registration_same_email_address = "User exists with same email id. Use different email address"


def change_password(user, password):
    user.set_password(password)
    user.save()
    user.userextended.last_updated_password_datetime = timezone.now()
    user.userextended.save()


def rand_alphanumeric(length=100):
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for _ in range(length))


def send_verification_email(user):

    try:
        result = EmailVerification.objects.get(user=user)
        # if verification code is not expired, send the same code
        if result.is_not_expired_email_verification():
            result.sent_datetime = timezone.now()               # reset the time
            result.save()
            verification_code = result.verification_code
        else:                                                   # if expired, delete the previous code
            result.delete()
            raise Exception
    except Exception:
        verification_code = rand_alphanumeric()
        EmailVerification.objects.create(user=user, verification_code=verification_code)

    email_msg = registration_email_verification
    email_msg += "http://127.0.0.1:8000" + \
                 reverse('accounts:verify',
                         kwargs={'verification_code': verification_code, 'username': user.username})
    send_mail('Verify your email', email_msg, settings_sensitive.EMAIL_HOST_USER, [user.email], fail_silently=True)


def register_view(request):
    # Same email alone is checked against the Users table
    def rand_from_name(f_name, l_name):
        return l_name[:3]+f_name[:3]+'_' + \
               ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for _ in range(6))

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['firstName']
            last_name = form.cleaned_data['lastName']
            while True:
                try:
                    username = rand_from_name(first_name.lower(), last_name.lower())          # generating username
                    user = User.objects.create_user(username, email=email, password=password)
                    break
                except Exception:
                    pass
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            UserExtended(user=user).save()
            send_verification_email(user)
            return render(request, "accounts/new_user_registered.html", {})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {'registerForm': form})


def login_view(request):
    # if this is a POST request we need to process the form data
    login_errors = []
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            if user is not None:
                # the password verified for the user
                if user.is_active:
                    if not user.userextended.is_email_verified:
                        return render(request, "accounts/email_not_verified.html", {})
                    login(request, user)
                    # print("User is valid, active and authenticated")
                    return HttpResponseRedirect(reverse('accounts:dashboard'))
                else:
                    return render(request, "accounts/account_disabled.html", {})
                    # print("The password is valid, but the account has been disabled!")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {'loginForm': form, 'login_errors': login_errors})


def send_forgot_password_verification_email(user):
    try:
        result = ForgotPasswordVerification.objects.get(user=user)
        # if verification code is not expired, send the same code
        if result.is_not_expired_forgot_password():
            result.sent_datetime = timezone.now()               # reset the time
            result.save()
            verification_code = result.verification_code
        else:                                                   # if expired, delete the previous code
            result.delete()
            raise Exception
    except Exception:
        verification_code = rand_alphanumeric()
        ForgotPasswordVerification.objects.create(user=user, verification_code=verification_code)

    email_msg = forgot_password_message
    email_msg += "http://127.0.0.1:8000" + reverse('accounts:forget_password_check')\
                 + "?verification_code=" + verification_code + '&username=' + user.username
    send_mail('Reset Password', email_msg, settings_sensitive.EMAIL_HOST_USER, [user.email], fail_silently=True)


@login_required()
def dashboard_view(request):

    return render(request, "accounts/dashboard.html", {})


@login_required()
def change_account_details_view(request):
    user = request.user
    data = {'firstName': user.first_name,
            'lastName': user.last_name,
            'countryCodePhoneNumber': user.userextended.country_code_phone_number,
            'phoneNumber': user.userextended.phone_number}
    if request.method == 'POST':
        form = AccountForm(request.POST, initial=data)
        if form.is_valid():
            user.first_name = form.cleaned_data['firstName']
            user.last_name = form.cleaned_data['lastName']
            user.userextended.country_code_phone_number = form.cleaned_data['countryCodePhoneNumber']
            user.userextended.phone_number = form.cleaned_data['phoneNumber']
            user.save()
            return render(request, "accounts/change_account_details.html", {'form': form, 'updated': True})

    else:
        form = AccountForm(initial=data)

    return render(request, "accounts/change_account_details.html", {'form': form})


@login_required()
def address_view(request):
    deleted = False
    if 'deleted' in request.GET:
        deleted = True
    address_list = Address.objects.filter(user=request.user)
    paginator = Paginator(address_list, 25)     # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        addresses = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        addresses = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        addresses = paginator.page(paginator.num_pages)

    return render(request, 'accounts/address.html', {'addresses': addresses, 'deleted': deleted})


@login_required()
def edit_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            contact_name = form.cleaned_data['contact_name']
            country_name = form.cleaned_data['country_name']
            city_name = form.cleaned_data['city_name']
            state_name = form.cleaned_data['state_name']
            street_address_line_1 = form.cleaned_data['street_address_line_1']
            street_address_line_2 = form.cleaned_data['street_address_line_2']
            zipcode = form.cleaned_data['zipcode']
            phone_number = form.cleaned_data['phone_number']
            country_code_phone_number = form.cleaned_data['country_code_phone_number']

            address.contact_name = contact_name
            address.country_name = country_name
            address.city_name = city_name
            address.state_name = state_name
            address.street_address_line_1 = street_address_line_1
            address.street_address_line_2 = street_address_line_2
            address.zipcode = zipcode
            address.phone_number = phone_number
            address.country_code_phone_number = country_code_phone_number
            address.last_updated_datetime = datetime.datetime.now()

            address.save()
            return HttpResponseRedirect(reverse('accounts:address'))
    else:
        form = AddressForm(instance=address)

    return render(request, "accounts/edit_address.html", {'form': form})


@login_required()
def delete_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    return HttpResponseRedirect(reverse("accounts:address") + '?deleted=true')


@login_required()
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('accounts:logout'))


def email_verification_check_view(request, verification_code, username):
    # in case user clicks more than one email verification link
    if request.user.is_authenticated() and request.user.userextended.is_email_verified:
        return HttpResponseRedirect(reverse('accounts:dashboard'))
    try:
        result = EmailVerification.objects.get(user__username=username, verification_code=verification_code)
        if not result.is_not_expired_email_verification:
            raise Exception
    except Exception:
        return render(request, "accounts/invalid_verification_email.html",{})

    user = User.objects.get(username=username)
    user.userextended.is_email_verified = True
    user.userextended.email_verified_datetime = timezone.now()
    user.userextended.save()
    result.delete()
    return render(request, "accounts/email_verified.html",{})


# (?P<username>[\w]*)/(?P<verification_code>[a-z0-9]*)
def forgot_password_check_view(request):
    if request.user.is_authenticated():   # only if the user didn't login
        return HttpResponseRedirect(reverse('accounts:dashboard'))

    verification_code, username = request.GET.get('verification_code'), request.GET.get('username')
    if verification_code is None or username is None:
        return render(request, "accounts/invalid_forgot_password_reset.html", {})
    else:
        try:
            result = ForgotPasswordVerification.objects.get(user__username=username,
                                                            verification_code=verification_code)
            if not result.is_not_expired_forgot_password:
                raise Exception
        except Exception:
            return render(request, "accounts/invalid_forgot_password_reset.html", {})

    user = User.objects.get(username=username)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ForgotPasswordForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            password = form.cleaned_data['password']
            change_password(user, password)
            result.delete()
            return render(request, "accounts/forgot_password_reset_done.html",{})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password_reset.html',
                  {'form': form, 'verification_code': verification_code, 'username': username})


def trouble_login_view(request):
    if request.user.is_authenticated():   # trouble login is for forgot password and resend verification alone
        return HttpResponseRedirect(reverse('accounts:dashboard'))
    return render(request, "accounts/trouble_login.html", {})


def forget_password_view(request):
    if request.user.is_authenticated():   # forgot password is only if user couldn't login
        return HttpResponseRedirect(reverse('accounts:dashboard'))
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EmailForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            if not user.userextended.is_email_verified:
                return render(request, "accounts/resend_verification_email.html", {'already_verified': False})
            send_forgot_password_verification_email(user)
            return render(request, "accounts/forgot_password.html", {'success': True})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EmailForm()

    return render(request, "accounts/forgot_password.html", {'form': form, 'already_verified': True})


def resend_verification_email_view(request):
    # if this is a POST request we need to process the form data
    if request.user.is_authenticated():       # only if the no user logged
        return HttpResponseRedirect(reverse('accounts:dashboard'))

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():

            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            if user.userextended.is_email_verified:
                return render(request, "accounts/resend_verification_email.html", {'already_verified': True})
            send_verification_email(user)
            return render(request, "accounts/resend_verification_email.html", {'success': True})

    else:
        form = EmailForm()

    return render(request, "accounts/resend_verification_email.html", {'form': form})


@login_required()
def change_password_view(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ChangePasswordForm(request.POST, user = request.user)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            new_password = form.cleaned_data['newPassword']
            change_password(request.user, new_password)
            logout(request)
            return render(request, "accounts/change_password_done.html", {})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, "accounts/change_password.html", {'form': form})


@login_required()
def new_address(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddressForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:

            contact_name = form.cleaned_data['contact_name']
            country_name = form.cleaned_data['country_name']
            city_name = form.cleaned_data['city_name']
            state_name = form.cleaned_data['state_name']
            street_address_line_1 = form.cleaned_data['street_address_line_1']
            street_address_line_2 = form.cleaned_data['street_address_line_2']
            zipcode = form.cleaned_data['zipcode']
            phone_number = form.cleaned_data['phone_number']
            country_code_phone_number = form.cleaned_data['country_code_phone_number']

            Address.objects.create(user=request.user, contact_name=contact_name,
                                   country_name=country_name, city_name=city_name,state_name=state_name,
                                   street_address_line_1=street_address_line_1,
                                   street_address_line_2=street_address_line_2, zipcode=zipcode,
                                   phone_number=phone_number,
                                   country_code_phone_number=country_code_phone_number,
                                   )

            return HttpResponseRedirect(reverse("accounts:address"))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AddressForm()

    return render(request, "accounts/new_address.html", {'form': form})
