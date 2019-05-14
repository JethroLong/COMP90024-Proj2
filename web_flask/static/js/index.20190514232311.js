(function(d){var h=[];d.loadImages=function(a,e){"string"==typeof a&&(a=[a]);for(var f=a.length,g=0,b=0;b<f;b++){var c=document.createElement("img");c.onload=function(){g++;g==f&&d.isFunction(e)&&e()};c.src=a[b];h.push(c)}}})(window.jQuery);
$.fn.hasAttr = function(name) { var attr = $(this).attr(name); return typeof attr !== typeof undefined && attr !== false; };


$(document).ready(function() {
r=function(){dpi=window.devicePixelRatio;$('.js').attr('src', (dpi>1) ? 'images/wechatimg1004-704.png' : 'images/wechatimg1004-352.png');
$('.js2').attr('src', (dpi>1) ? 'images/wechatimg1004-704.png' : 'images/wechatimg1004-352.png');
$('.js3').attr('src', (dpi>1) ? 'images/wechatimg1004-704.png' : 'images/wechatimg1004-352.png');
$('.js4').attr('src', (dpi>1) ? 'images/wechatimg1004-704.png' : 'images/wechatimg1004-352.png');
$('.js5').attr('src', (dpi>1) ? 'images/screen-shot-2019-05-14-at-9.30.13-pm-1260.jpg' : 'images/screen-shot-2019-05-14-at-9.30.13-pm-630.jpg');
$('.js6').attr('src', (dpi>1) ? 'images/screen-shot-2019-05-14-at-9.30.13-pm-1260.jpg' : 'images/screen-shot-2019-05-14-at-9.30.13-pm-630.jpg');
$('.js7').attr('src', (dpi>1) ? 'images/screen-shot-2019-05-14-at-9.33.28-pm-1152.jpg' : 'images/screen-shot-2019-05-14-at-9.33.28-pm-576.jpg');
$('.js8').attr('src', (dpi>1) ? 'images/4173109-1304.jpg' : 'images/4173109-652.jpg');
$('.js9').attr('src', (dpi>1) ? 'images/4173109-1304.jpg' : 'images/4173109-652.jpg');};
if(!window.HTMLPictureElement){r();}
(function(){$('a[href^="#"]:not(.allowConsent,.noConsent,.denyConsent,.removeConsent)').each(function(){$(this).click(function(){var t=this.hash.length>1?$('[name="'+this.hash.slice(1)+'"]').offset().top:0;return $("html, body").animate({scrollTop:t},400),!1})})})();

});