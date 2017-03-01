from rest_framework.generics import ListAPIView
from .serializers import StockSerializer
from stocks.models import StockHistory

class StockListAPIView(ListAPIView):
	queryset = StockHistory.objects.filter(watch_list=1)
	serializer_class = StockSerializer
