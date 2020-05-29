/*
 * Iran Map - SVG and Responsive.
 * Free and open source.
 * Version 1.1.0
 * By: MohammadReza Pourmohammad.
 * Email: mohammadrpm@gmail.com
 * Web: http://mrpm.ir
 */

$(function() {

    $(window).resize(function() {
        resposive();
    });

    function resposive() {
        var height = $('#IranMap .list').height();
        var width = $('#IranMap .list').width();
        if (height > width) {
            $('#IranMap svg').height(width).width(width);
        } else {
            $('#IranMap svg').height(height).width(height);
        }
    }
    resposive();

    $('#IranMap svg g path').hover(function() {
        var className = $(this).attr('class');
        var parrentClassName = $(this).parent('g').attr('class');
        var itemName = $('#IranMap .list .' + parrentClassName + ' .' + className + ' a').html();
        if (itemName) {
            $('#IranMap .list .' + parrentClassName + ' .' + className + ' a').addClass('hover');
            $('#IranMap .show-title').html(itemName).css({'display': 'block'});
        }
    }, function() {
        $('#IranMap .list a').removeClass('hover');
        $('#IranMap .show-title').html('').css({'display': 'none'});
    });

    $('#IranMap .list ul li ul li a').hover(function() {
        var className = $(this).parent('li').attr('class');
        var parrentClassName = $(this).parent('li').parent('ul').parent('li').attr('class');
        var object = '#IranMap svg g.' + parrentClassName + ' path.' + className;
        var currentClass = $(object).attr('class');
        $(object).attr('class', currentClass + ' hover');
    }, function() {
        var className = $(this).parent('li').attr('class');
        var parrentClassName = $(this).parent('li').parent('ul').parent('li').attr('class');
        var object = '#IranMap svg g.' + parrentClassName + ' path.' + className;
        var currentClass = $(object).attr('class');
        $(object).attr('class', currentClass.replace(' hover', ''));
    });

    $('#IranMap').mousemove(function(e) {
        var posx = 0;
        var posy = 0;
        if (!e)
            var e = window.event;
        if (e.pageX || e.pageY) {
            posx = e.pageX;
            posy = e.pageY;
        } else if (e.clientX || e.clientY) {
            posx = e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
            posy = e.clientY + document.body.scrollTop + document.documentElement.scrollTop;
        }
        if ($('#IranMap .show-title').html()) {
            var offset = $(this).offset();
            var x = (posx - offset.left + 25) + 'px';
            var y = (posy - offset.top - 5) + 'px';
            $('#IranMap .show-title').css({'left': x, 'top': y});
        }
    });

});