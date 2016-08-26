function updateStockPrice() {
    var symbols = '';
    $.each($('div.symbol'), function (index, value) {
        symbols += 'NSE:' + $(value).attr('data-symbol') + ',';
    });

    if (!symbols) return;

    var google_finance_url = "http://finance.google.com/finance/info?client=ig&q=" + symbols;

    $.ajax({
        crossDomain: true,
        type: 'GET',
        contentType: "application/json; charset=utf-8",
        url: google_finance_url,
        dataType: "jsonp",
        success: function (data) {
            $.each(data, function (index, value) {
                $("." + value.t + '-current-price').text(value.l);
                var todayChangeSpan = $('.' + value.t + '-today-change'),
                    todayChangePrice = parseFloat(value.c);
                todayChangeSpan.text(todayChangePrice);
                changePriceColor(todayChangePrice, todayChangeSpan);
                var overallGainDiv = $("." + value.t + '-overall-gain');
                var overallGainPrice = (value.l) - overallGainDiv.attr('data-close');
                var overallGainPercent = overallGainPrice/ (overallGainDiv.attr('data-close')/100);
                $('.' + value.t + '-overall-gain-percent').text('(' + overallGainPercent.toFixed(2) + '%)');
                overallGainDiv.text(overallGainPrice.toFixed(2));
                changePriceColor(overallGainPrice, overallGainDiv);
            });
        }
    });
}

function changePriceColor(price, domElement) {
    if(price > 0) {
        domElement.css('color', '#3a6c00');
        domElement.addClass('glyphicon').addClass('glyphicon-arrow-up');
    }
    else {
        domElement.css('color', '#c51010');
        domElement.addClass('glyphicon').addClass('glyphicon-arrow-down');
    }
}


$(function () {
    // Update the current stock price after DOM loaded
    updateStockPrice();
    $("time.timeago").timeago();

    $('.symbol').click(function (e) {
        loadDeliverables(this.dataset.symbol, this.dataset.tradedate);
    })

});

var today_date_time = new Date();
var today_day = today_date_time.getDay();
var present_time = today_date_time.getHours();

if (((today_day != 0) && (today_day != 6)) && ((present_time < 16) && (present_time > 9))){
    setInterval(function() {
        updateStockPrice();
    }, 5000);
}

function loadDeliverables(symbol, from_date, to_date) {
     $("#deliveryModal .modal-title").html(symbol);
    $.ajax({
        url: '/api/deliverables/',
        data: {symbol: symbol, from_date: from_date, to_date:to_date}
    }).done(function (data) {
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
            width: 900,
            yaxis: {title: 'Deliverables',
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
    });
}