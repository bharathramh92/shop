from django.conf.urls import url
from listing import views

urlpatterns = [
    url(r'^$', views.index_view, name="index"),
    url(r'^department/(?P<department_id>[0-9]+)/$', views.department_view, name="department"),
    url(r'^department/$', views.all_department_view, name="all_department"),
    url(r'^Books/(?P<pk>[0-9]+)/$', views.book_item, name="book_item"),

    url(r'^search/$', views.search_view, name="search"),

    url(r'listing/(?P<slug>[\w-]+)/$', views.listing_item_view, name="listing_item")
]
