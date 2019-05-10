(function(d) {
    var h = [];
    d.loadImages = function(a, e) {
        "string" == typeof a && (a = [a]);
        for (var f = a.length, g = 0, b = 0; b < f; b++) {
            var c = document.createElement("img");
            c.onload = function() {
                g++;
                g == f && d.isFunction(e) && e()
            };
            c.src = a[b];
            h.push(c)
        }
    }
})(window.jQuery);
$.fn.hasAttr = function(name) {
    var attr = $(this).attr(name);
    return typeof attr !== typeof undefined && attr !== false;
};
loadGoogleMaps = function() {
    var mapOptions = {
        zoom: 11,
        center: new google.maps.LatLng(40.6700, -73.9400),
        mapTypeId: google.maps.MapTypeId.ROADMAP,
    };
    var map = new google.maps.Map($('.js4').get(0), mapOptions);
};
$(document).ready(function() {
    r = function() {
        dpi = window.devicePixelRatio;
        $('.js').attr('src', (dpi > 1) ? 'images/1284512-1278.jpg' : 'images/1284512-639.jpg');
        $('.js2').attr('src', (dpi > 1) ? 'images/1284512-1278.jpg' : 'images/1284512-639.jpg');
        $('.js3').attr('src', (dpi > 1) ? 'images/1284512-1278.jpg' : 'images/1284512-639.jpg');
    };
    if (!window.HTMLPictureElement) {
        r();
    }
    (function() {
        $('a[href^="#"]:not(.allowConsent,.noConsent,.denyConsent,.removeConsent)').each(function() {
            $(this).click(function() {
                var t = this.hash.length > 1 ? $('[name="' + this.hash.slice(1) + '"]').offset().top : 0;
                return $("html, body").animate({
                    scrollTop: t
                }, 400), !1
            })
        })
    })();
    initMenu($('#m1')[0]);
    var s = document.createElement('web_server.py');
    s.type = 'text/javascript';
    s.src = 'https://maps.googleapis.com/maps/api/js';
    s.onload = loadGoogleMaps;
    document.body.appendChild(s);
});