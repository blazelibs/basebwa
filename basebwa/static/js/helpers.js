// JavaScript Document

String.prototype.trim = function() {
	return this.replace(/^[\s\xA0]+|[\s\xA0]+$/g,"");
}
String.prototype.ltrim = function() {
	return this.replace(/^[\s\xA0]+/,"");
}
String.prototype.rtrim = function() {
	return this.replace(/[\s\xA0]+$/,"");
}
String.prototype.fileExt = function( include_dot ) {
	return fileExt( this, include_dot )
}

function trim(stringToTrim) {
	return stringToTrim.replace(/^[\s\xA0]+|[\s\xA0]+$/g,"");
}
function ltrim(stringToTrim) {
	return stringToTrim.replace(/^[\s\xA0]+/,"");
}
function rtrim(stringToTrim) {
	return stringToTrim.replace(/[\s\xA0]+$/,"");
}

function isInt(x) {
   var y=parseInt(x);
   if (isNaN(y)) return false;
   return x==y && x.toString()==y.toString();
}

function fileExt( str_path, include_dot ) {
    include_dot = typeof(include_dot) != 'undefined' ? include_dot : false; 
    
    var shift = include_dot ? 0 : 1;
    
    var dot = str_path.lastIndexOf(".")
    if( dot == -1 ) {
        return '';
    }
    return str_path.substr(dot + shift); 
}

function isNumeric(x) {
    if( x.trim() == "" ) {
        return false;
    }
// I use this function like this: if (isNumeric(myVar)) { }
// regular expression that validates a value is numeric
var RegExp = /^(-)?(\d*)(\.?)(\d*)$/; // Note: this WILL allow a number that ends in a decimal: -452.
// compare the argument to the RegEx
// the 'match' function returns 0 if the value didn't match
var result = x.match(RegExp);
return result;
}

/********************************* Number Format Function *******************/
function numberFormat(num) {
num = num.toString().replace(/\$|\,/g,'');
if(isNaN(num))
num = "0";
sign = (num == (num = Math.abs(num)));
num = Math.floor(num*100+0.50000000001);
cents = num%100;
num = Math.floor(num/100).toString();
if(cents<10)
cents = "0" + cents;
for (var i = 0; i < Math.floor((num.length-(1+i))/3); i++)
num = num.substring(0,num.length-(4*i+3))+','+
num.substring(num.length-(4*i+3));
return (((sign)?'':'-') + num + '.' + cents);
}

/********************************* Date Format Functions ********************/
//http://www.expertsrt.com/scripts/Rod/validate_date.php
function isDate( value ) {
    var RegExPattern = /^(?=\d)(?:(?:(?:(?:(?:0?[13578]|1[02])(\/|-|\.)31)\1|(?:(?:0?[1,3-9]|1[0-2])(\/|-|\.)(?:29|30)\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})|(?:0?2(\/|-|\.)29\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))|(?:(?:0?[1-9])|(?:1[0-2]))(\/|-|\.)(?:0?[1-9]|1\d|2[0-8])\4(?:(?:1[6-9]|[2-9]\d)?\d{2}))($|\ (?=\d)))?(((0?[1-9]|1[012])(:[0-5]\d){0,2}(\ [AP]M))|([01]\d|2[0-3])(:[0-5]\d){1,2})?$/;
    
    if ((value.match(RegExPattern)) && (value!='')) {
        return true;
    } else {
        return false;
    } 
}
