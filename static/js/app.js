function updateStockPrice() {
    var symbols = '';

    $.each($('a.symbol'), function (index, value) {
        symbols += $(value).attr('data-symbol') + ',';
    });

    if (!symbols){
        return
    }
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
    $('[data-toggle="tooltip"]').tooltip();
});

var today_date_time = new Date();
var today_day = today_date_time.getDay();
var present_time = today_date_time.getHours();

if (((today_day != 0) && (today_day != 6)) && ((present_time < 16) && (present_time > 9))){
    setInterval(function() {
    updateStockPrice();
}, 5000);

}

else{

}



























// function posthttp(symbol){
//     var myVar = setInterval(function(){httpGet(symbol)}, 5000);
//
//     return myVar;
// }
//
//
// function httpGet(symbol)
//         {
//             var xmlHttp = new XMLHttpRequest();
//             var Url = "http://finance.google.com/finance/info?client=ig&q="+ symbol;
//             xmlHttp.open("GET", Url, false);
//             xmlHttp.send(null);
//             var myArr = xmlHttp.responseText;
//
//              var txt = myArr.replace("// [","");
//              var asd = /]/g;
//              var qwerq = txt.replace(asd,"");
//
//
//              var obj = JSON.parse(qwerq);
//            //  document.write(obj);
//              return obj;
// //             return obj;
//
//         }
//
// function karthi(){
//         document.write("sdfasdfsadgdfgfg");
//         //alert("asdfdsf");
// }
// //function posthttp(symbol){
// //
// //       var myVar = setInterval(function(){ httpGet(symbol) }, 3000);
// //       document.write(myVar);
// //        return myVar;
// //        }

// $(function() {
//     console.log( "ready!" );
// });
