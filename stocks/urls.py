from . import views, api

from django.conf.urls import url

urlpatterns = [url(r'^$', views.index, name='index'),
               url(r'^history/$', views.stock_history_view, name='history'),
               url(r'^api/deliverables/$', api.deliverable_api, name='deliverables_api'),
               url(r'^api/watchlist/remove/$', api.watchlist_remove, name='watchlist_remove_api'),
               url(r'^api/watchlist/add/$', api.watchlist_add, name='watchlist_add_api'),
               url(r'^api/symbols/$', api.list_symbols, name='list_symbols'),
               url(r'^api/stockQuotes/$', api.stock_quotes, name='stock_quotes')
               ]
