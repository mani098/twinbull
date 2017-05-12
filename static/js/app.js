$(function () {
    // Update the current stock price after DOM loaded
    updateStockPrice();

    $("#datepicker").datepicker();
});

var today_date_time = new Date();
var today_day = today_date_time.getDay();
var present_time = today_date_time.getHours();

if (((today_day !== 0) && (today_day !== 6)) && (16 > present_time > 9)) {
    setInterval(function () {
        updateStockPrice();
    }, 1000 * 60);
}

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
            renderStockDetails(data);
        }
    });
}

function renderStockDetails(data) {
    var avgGain = 0;
    var totalStockClosePrice = 0;
    var avgLastPrice = 0;
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
        var avgClosePrice = toFloat(overallGainDiv.attr('data-close'));
        var overallGainPrice = toFloat(lastPrice - avgClosePrice);
        var overallGainPercent = toFloat(overallGainPrice / (avgClosePrice / 100));
        avgLastPrice += toFloat(lastPrice);
        avgGain += toFloat(overallGainPrice);
        totalStockClosePrice += avgClosePrice;

        var predictedPrice = getTargetStopLoss(avgClosePrice);
        $('.' + symbol + '-trg-price').text(predictedPrice.target);
        $('.' + symbol + '-stop-loss-price').text(predictedPrice.stopLoss);
        $('.' + symbol + '-overall-gain-percent').text('(' + overallGainPercent + '%)');
        overallGainDiv.text(overallGainPrice);
        changePriceColor(overallGainPrice, overallGainDiv);
    });
    var avgGainPercent = (100 / totalStockClosePrice * (avgLastPrice - totalStockClosePrice));
    var $avgGainPrt = $('.avg-gain-prt');
    var $avgGain = $('.avg-gain');
    $avgGainPrt.text(toFloat(avgGainPercent) + '%');
    $avgGain.text(toFloat(avgGain));
    $('.tot-inst-price').text(toFloat(totalStockClosePrice));
    changePriceColor(avgGainPercent, $avgGainPrt);
    changePriceColor(avgGain, $avgGain);
}

function changePriceColor(price, domElement) {
    if (price > 0 || !price) {
        domElement.css('color', '#00cc00');
    }
    else {
        domElement.css('color', '#ff0000');
    }
}

function toFloat(n) {
    var tmp = parseFloat(n);
    return parseFloat(tmp.toFixed(2));
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