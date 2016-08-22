from . import views

from django.conf.urls import url

urlpatterns = [url(r'^$', views.index, name='index'),
               url(r'^history/$', views.stock_history_view, name='history'),
               url(r'^deliverables/$', views.stocks_deliverables, name='deliverables'),
               ]
