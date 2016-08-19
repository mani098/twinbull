function updateStockPrice() {
    var symbols = '';

    $.each($('a.symbol'), function (index, value) {
        symbols += $(value).attr('data-symbol') + ',';
    });

    var google_finance_url = "http://finance.google.com/finance/info?client=ig&q=" + symbols;

    $.get(google_finance_url, function(data, status){
        var stock_data = JSON.parse(data.slice(3));
        $.each(stock_data, function (index, value) {
            $("#" + value.t + '-current-price').text(value.l);
            var todayChangeSpan = $('#' + value.t + '-today-change'),
                todayChangePrice = parseFloat(value.c);
            todayChangeSpan.text(todayChangePrice);
            if(todayChangePrice > 0) {
                todayChangeSpan.css('color', 'green');
                todayChangeSpan.addClass('glyphicon-arrow-up');
            }
            else {
                todayChangeSpan.css('color', 'red');
                todayChangeSpan.addClass('glyphicon-arrow-down');
            }
        })
    });
}


$(function () {
    updateStockPrice();
});


setInterval(function() {
    updateStockPrice();
}, 5000);



























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
