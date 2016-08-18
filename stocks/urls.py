from . import views

from django.conf.urls import url

urlpatterns = [url(r'^$', views.index, name='index'),
               url(r'^add/$', views.add_watch_list, name='add'),
               ]
