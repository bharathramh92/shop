from django.conf.urls import url
from seller import views
from seller.views import PublisherAutocomplete, AuthorAutocomplete

urlpatterns = [

    url(r'^$', views.dashboard_view, name="dashboard"),
    url(r'^orders/$', views.orders_view, name="orders"),

    url(r'^new/$', views.new_view, name="new"),
    url(r'^inventory/add$', views.new_inventory_view, name="new_inventory"),
    url(r'^inventory/edit/(?P<pk>[0-9]+)/$', views.edit_inventory_view, name="edit_inventory"),

    url(
        r'^author-autocomplete/$',
        AuthorAutocomplete.as_view(),
        name='author-autocomplete',
    ),
    url(
        r'^publisher-autocomplete/$',
        PublisherAutocomplete.as_view(),
        name='publisher-autocomplete',
    ),

    url(r'^new/book/add_author$', views.new_author, name="new_author"),
    url(r'^new/book/add_publisher$', views.new_publisher, name="new_publisher"),
    url(r'^new/book/(?P<isbn>[0-9]*)/$', views.add_new_book, name="new_book"),
    url(r'^new/book/$', views.add_new_book_pk_check, name="new_book_check"),


]
