setInterval(function() {
  //Get all symbols and construct a comma seperated string

  $.get("http://finance.google.com/finance/info?client=ig&q=SBIN,HCL", function(data, status){
        alert("Data: " + data + "\nStatus: " + status);
    });

}, 5000);
function posthttp(symbol){
    var myVar = setInterval(function(){httpGet(symbol)}, 5000);

    return myVar;
}


function httpGet(symbol)
        {
            var xmlHttp = new XMLHttpRequest();
            var Url = "http://finance.google.com/finance/info?client=ig&q="+ symbol;
            xmlHttp.open("GET", Url, false);
            xmlHttp.send(null);
            var myArr = xmlHttp.responseText;

             var txt = myArr.replace("// [","");
             var asd = /]/g;
             var qwerq = txt.replace(asd,"");


             var obj = JSON.parse(qwerq);
           //  document.write(obj);
             return obj;
//             return obj;

        }

function karthi(){
        document.write("sdfasdfsadgdfgfg");
        //alert("asdfdsf");
}
//function posthttp(symbol){
//
//       var myVar = setInterval(function(){ httpGet(symbol) }, 3000);
//       document.write(myVar);
//        return myVar;
//        }