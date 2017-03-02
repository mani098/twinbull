$(function () {
    // Update the current stock price after DOM loaded
    updateStockPrice();
    $("time.timeago").timeago();

    // $('.symbol').click(function (e) {
    //     e.preventDefault();
    //     loadDeliverables(this.dataset.symbol, this.dataset.tradedate);
    // });
    $("#datepicker").datepicker();

    // $.ajax({
    //     url: '/api/symbols/',
    //     type: 'GET'
    // }).done(function (responseData) {
    //     $("#symbol-tag").autocomplete({
    //         source: responseData.symbols
    //     });
    // });
});

$('span.add-btn').click(function () {
    var rowId = this.dataset.rowId;
    var comment = document.getElementById(rowId).value;
    this.className = "glyphicon glyphicon-ok ok-btn";

    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        url: '/api/watchlist/add/',
        data: JSON.stringify({row_id: rowId, comments: comment})
    });

});


$('.remove-btn').click(function () {
    var rowId = this.dataset.rowId;
    $(this).parents('tr').remove();
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        url: '/api/watchlist/remove/',
        data: JSON.stringify({row_id: rowId}),
        error: function () {
            alert("Some error occurred")
        }
    });
});

function updateStockPrice() {
    var stock_ids = '';
    $.each($('div.symbol'), function (index, value) {
        stock_ids += $(value).attr('data-stock-id') + ',';
    });

    if (!stock_ids) return;

    var stockQuotes_url = '/api/stockQuotes?stock_ids=' + stock_ids;

    $.ajax({
        type: 'GET',
        contentType: "application/json; charset=utf-8",
        url: stockQuotes_url,
        success: function (data) {
            $.each(data['data'], function (index, value) {
                var lastPrice = value.lastPrice;
                var symbol = value.symbol
                $("." + symbol + '-current-price').text(lastPrice);
                var todayChangeSpan = $('.' + symbol + '-today-change'),
                    todayChangePrice = parseFloat(value.change);
                todayChangeSpan.text(todayChangePrice);
                changePriceColor(todayChangePrice, todayChangeSpan);
                var overallGainDiv = $("." + symbol + '-overall-gain');
                var overallGainPrice = (lastPrice) - overallGainDiv.attr('data-close');
                var overallGainPercent = overallGainPrice / (overallGainDiv.attr('data-close') / 100);
                $('.' + symbol + '-overall-gain-percent').text('(' + overallGainPercent.toFixed(2) + '%)');
                overallGainDiv.text(overallGainPrice.toFixed(2));
                changePriceColor(overallGainPrice, overallGainDiv);
            });
        }
    });
}

function changePriceColor(price, domElement) {
    if (price > 0 || price == NaN) {
        domElement.css('color', '#3a6c00');
        domElement.addClass('glyphicon').addClass('glyphicon-arrow-up');
    }
    else {
        domElement.css('color', '#c51010');
        domElement.addClass('glyphicon').addClass('glyphicon-arrow-down');
    }
}

var today_date_time = new Date();
var today_day = today_date_time.getDay();
var present_time = today_date_time.getHours();

if (((today_day != 0) && (today_day != 6)) && ((present_time < 16) && (present_time > 9))) {
    setInterval(function () {
        updateStockPrice();
    }, 25000);
}

function loadDeliverables(symbol, from_date, to_date) {
    $("#deliveryModal .modal-title").html(symbol);
    $.ajax({
        url: '/api/deliverables/',
        type: 'GET',
        data: {symbol: symbol, trade_date: from_date, to_date: to_date},
        success: function (data) {
            var x = [], y_deliverables = [], y_price = [];
            $.each(data['data'], function (index, value) {
                x.push(value.trade_date);
                y_deliverables.push(value.deliverables);
                y_price.push(value.close);
            });
            var traceDeliverables =
                {
                    x: x,
                    y: y_deliverables,
                    name: 'Deliverables',
                    type: 'scatter'
                };
            var tracePrice =
                {
                    x: x,
                    y: y_price,
                    yaxis: 'y2',
                    name: 'Price',
                    type: 'scatter'
                };
            var plotlyData = [traceDeliverables, tracePrice];
            var layout = {
                width: 1100,
                height: 600,
                yaxis: {
                    title: 'Deliverables',
                    titlefont: {color: '#1f77b4'},
                    tickfont: {color: '#1f77b4'}
                },
                yaxis2: {
                    title: 'Price',
                    titlefont: {color: 'rgb(148, 103, 189)'},
                    tickfont: {color: 'rgb(148, 103, 189)'},
                    overlaying: 'y',
                    side: 'right' //,
                }
            };
            Plotly.newPlot("plotly-deliverables", plotlyData, layout);
            $('#deliveryModal').modal();
        }
    });
}