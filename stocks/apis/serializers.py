from rest_framework import serializers

from stocks.models import StockHistory


class StockSerializer(serializers.ModelSerializer):
	class Meta:
		model = StockHistory
		fields = [
			'stock',
			'trade_date',
			'watch_list',
			'is_filtered'
		]
