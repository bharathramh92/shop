from django.conf.urls import include, url
from accounts import views

urlpatterns = [

    url(r'^login/$', views.login_view, name="login"),
    url(r'^register/$', views.register_view, name="register"),
    url(r'^logout/$', views.logout_view, name="logout"),

    url(r'^$', views.dashboard_view, name="dashboard"),

    url(r'^verify/(?P<username>[\w]*)/(?P<verification_code>[a-z0-9]*)/$', views.email_verification_check_view,
        name="verify"),
    url(r'^trouble_login/$', views.trouble_login_view, name="trouble_login"),
    url(r'^forget_password/$', views.forget_password_view, name="forget_password"),
    url(r'^forget_password/reset/$', views.forgot_password_check_view, name="forget_password_check"),
    url(r'^resend_verification_email/$', views.resend_verification_email_view, name="resend_verification_email"),

    url(r'^change_password/$', views.change_password_view, name="change_password"),
    url(r'^new_address/$', views.new_address, name="new_address"),
    url(r'^address/$', views.address_view, name="address"),
    url(r'^edit_address/(?P<pk>[0-9]*)$', views.edit_address_view, name="edit_address"),
    url(r'^delete_address/(?P<pk>[0-9]*)$', views.delete_address_view, name="delete_address"),

    url(r'^change_account_details/$', views.change_account_details_view, name="change_account_details"),

]
