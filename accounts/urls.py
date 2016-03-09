from django.conf.urls import include, url
from accounts import views

urlpatterns = [

    url(r'^login/$', views.login_view, name="login"),
    url(r'^register/$', views.register_view, name="register"),
    url(r'^logout/$', views.logout_view, name="logout"),
    url(r'^$', views.dashboard_view, name="dashboard"),

    url(r'^verify/(?P<username>[\w]*)/(?P<verification_code>[a-z0-9]*)/$', views.email_verification_check_view,
        name="verify"),
    url(r'^troubleLogin/$', views.trouble_login_view, name="trouble_login"),
    url(r'^forgetPassword/$', views.forget_password_view, name="forget_password"),
    url(r'^forgetPassword/reset/$', views.forgot_password_check_view, name="forget_password_check"),
    url(r'^resendVerificationEmail/$', views.resend_verification_email_view, name="resend_verification_email"),

    url(r'^changePassword/$', views.change_password_view, name="change_password"),
    url(r'^newAddress/$', views.new_address, name="new_address"),

]
