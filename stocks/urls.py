from . import views

from django.conf.urls import url

urlpatterns = [url(r'^$', views.index, name='index'),
               url(r'^history/$', views.stock_history_view, name='history'),
               ]
