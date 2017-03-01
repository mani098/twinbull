from .views import StockListAPIView

from django.conf.urls import url

urlpatterns = [
				url(r'^$', StockListAPIView.as_view(), name='list'),

               ]
