from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import StockSerializer
from stocks.models import StockHistory


class Stockapiview(viewsets.ViewSet):

	def list(self, request):
		queryset = StockHistory.objects.filter(watch_list=1)
		serializer_class = StockSerializer(queryset, many=True)

		query = request.GET.get("trade_date")
		if query:
			queryset = queryset.filter(trade_date=query)
			serializer_class = StockSerializer(queryset, many=True)

		return Response(serializer_class.data)

	def partial_update(self, request, pk=None):
		stock = StockHistory.objects.get(pk=pk)
		stock.watch_list = request.data['watch_list']
		stock.save()
		return Response()



