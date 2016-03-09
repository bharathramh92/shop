from django.conf.urls import url
from category_tree import views

urlpatterns = [

    url(r'^reset/$', views.reset_view, name="reset"),

]
