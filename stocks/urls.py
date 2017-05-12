from . import views, api

from django.conf.urls import url

urlpatterns = [url(r'^$', views.IndexView.as_view(), name='index'),
               url(r'^api/stockQuotes/$', api.stock_quotes, name='stock_quotes')
               ]
