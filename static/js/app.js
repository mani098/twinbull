$(function () {
    // Update the current stock price after DOM loaded
    updateStockPrice();

    $("#datepicker").datepicker();
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

    $('.ovl-gn, .ltp-gn, .org-name').html('<img class="pre-loader-gif" src="/static/img/pre-loader.gif">');

    var stockQuotes_url = '/api/stockQuotes?stock_ids=' + stock_ids;
    $.ajax({
        type: 'GET',
        contentType: "application/json; charset=utf-8",
        url: stockQuotes_url,
        success: function (data) {
            $.each(data['data'], function (index, value) {
                var lastPrice = value['lastPrice'].replace(',', '');
                var symbol = value['symbol'];
                $("." + symbol + '-current-price').text(lastPrice);

                // Add company name
                $('td[data-company-id=' + symbol + ']').text(value['companyName']);

                var todayChangeSpan = $('.' + symbol + '-today-change'),
                    todayChangePrice = parseFloat(value.change);
                todayChangeSpan.text(todayChangePrice + ' (' + value['pChange'] + '%)');
                changePriceColor(todayChangePrice, todayChangeSpan);
                var overallGainDiv = $("." + symbol + '-overall-gain');
                var avgClosePrice = overallGainDiv.attr('data-close');
                var overallGainPrice = lastPrice - avgClosePrice;
                var overallGainPercent = overallGainPrice / (avgClosePrice / 100);

                var predictedprice = getTargetStopLoss(avgClosePrice);
                $('.' + symbol + '-trg-price').text(predictedprice.target);
                $('.' + symbol + '-stop-loss-price').text(predictedprice.stopLoss);


                $('.' + symbol + '-overall-gain-percent').text('(' + overallGainPercent.toFixed(2) + '%)');
                overallGainDiv.text(overallGainPrice.toFixed(2));
                changePriceColor(overallGainPrice, overallGainDiv);
            });
        }
    });
}

function changePriceColor(price, domElement) {
    if (price > 0 || price === NaN) {
        domElement.css('color', '#00cc00');
        // domElement.prepend('<span></span>');
        // domElement.find('span').addClass('glyphicon').addClass('glyphicon-arrow-up');
    }
    else {
        domElement.css('color', '#ff0000');
        // domElement.prepend('<span></span>');
        // domElement.find('span').addClass('glyphicon').addClass('glyphicon-arrow-down');
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
$('.symbol').click(function (event) {
    var doc = document;
    var text = this;
    var range;

    if (doc.body.createTextRange) { // ms
        range = doc.body.createTextRange();
        range.moveToElementText(text);
        range.select();
    }
    else if (window.getSelection) { // moz, opera, webkit
        var selection = window.getSelection();
        range = doc.createRange();
        range.selectNodeContents(text);
        selection.removeAllRanges();
        selection.addRange(range);
    }
    document.execCommand('copy');

});

function getTargetStopLoss(price) {
    var targetPrice = parseFloat(price) + parseFloat((price / 100) * 3); // +3% target
    var stopLoss = parseFloat(price) + parseFloat((price / 100) * -2); // -2% stopLoss
    return {target: targetPrice.toFixed(1), stopLoss: stopLoss.toFixed(1)};
}