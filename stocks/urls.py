from . import views, api

from django.conf.urls import url

urlpatterns = [url(r'^$', views.index, name='index'),
               url(r'^history/$', views.stock_history_view, name='history'),
               url(r'^api/deliverables/$', api.deliverable_api, name='deliverables-api'),
               url(r'^api/watchlist/remove/$', api.watchlist_remove, name='watchlist-remove-api')
               ]
