jQuery(document).ready(function() {
    "use strict";
    /*  Menu */
    jQuery(".toggle").on("click", function() {
        return jQuery(".submenu").is(":hidden") ? jQuery(".submenu").slideDown("fast") : jQuery(".submenu").slideUp("fast"), !1
    }), jQuery(".topnav").accordion({
        accordion: !1,
        speed: 300,
        closedSign: "+",
        openedSign: "-"
    }), jQuery("#nav > li").hover(function() {
        var e = $(this).find(".level0-wrapper");
        e.hide(), e.css("left", "0"), e.stop(true, true).delay(150).fadeIn(300, "easeOutCubic")
    }, function() {
        jQuery(this).find(".level0-wrapper").stop(true, true).delay(300).fadeOut(300, "easeInCubic")
    });
    jQuery("#nav li.level0.drop-menu").mouseover(function() {
            return jQuery(window).width() >= 740 && jQuery(this).children("ul.level1").fadeIn(100), !1
        }).mouseleave(function() {
            return jQuery(window).width() >= 740 && jQuery(this).children("ul.level1").fadeOut(100), !1
        }), jQuery("#nav li.level0.drop-menu li").mouseover(function() {
            if (jQuery(window).width() >= 740) {
                jQuery(this).children("ul").css({
                    top: 0,
                    left: "165px"
                });
                var e = jQuery(this).offset();
                e && jQuery(window).width() < e.left + 325 ? (jQuery(this).children("ul").removeClass("right-sub"), jQuery(this).children("ul").addClass("left-sub"), jQuery(this).children("ul").css({
                    top: 0,
                    left: "-167px"
                })) : (jQuery(this).children("ul").removeClass("left-sub"), jQuery(this).children("ul").addClass("right-sub")), jQuery(this).children("ul").fadeIn(100)
            }
        }).mouseleave(function() {
            jQuery(window).width() >= 740 && jQuery(this).children("ul").fadeOut(100)
        }),

        /* Mobile Menu */

        jQuery("#mobile-menu").mobileMenu({
            MenuWidth: 250,
            SlideSpeed: 300,
            WindowsMaxWidth: 767,
            PagePush: !0,
            FromLeft: !0,
            Overlay: !0,
            CollapseMenu: !0,
            ClassName: "mobile-menu"
        }),


    /*========== offer slide ===========*/



    jQuery(function() {

        jQuery("#slideshow > p:gt(0)").hide();

        setInterval(function() {
            jQuery('#slideshow > p:first')
                .fadeOut(1000)
                .next()
                .fadeIn(1000)
                .end()
                .appendTo('#slideshow');
        },  3000);

    });

	if(jQuery('#featured-slider').length > 0){
	
		/* Featured slider */
		jQuery("#featured-slider .slider-items").owlCarousel({
			items: 4, //10 items above 1000px browser width
			itemsDesktop: [1024, 3], //5 items between 1024px and 901px
			itemsDesktopSmall: [980, 2], // 3 items betweem 900px and 601px
			itemsTablet: [768, 2], //2 items between 600 and 0;
			itemsMobile: [360, 1],
			navigation: false,
			navigationText: ["<a class=\"flex-prev\"></a>", "<a class=\"flex-next\"></a>"],
			slideSpeed: 500,
			pagination: true
		});
	}
	
	if(jQuery('#trending-slider').length > 0){
		/* Trending slider */
		jQuery("#trending-slider .slider-items").owlCarousel({
			items: 4, //10 items above 1000px browser width
			itemsDesktop: [1024, 3], //5 items between 1024px and 901px
			itemsDesktopSmall: [980, 2], // 3 items betweem 900px and 601px
			itemsTablet: [768, 2], //2 items between 600 and 0;
			itemsMobile: [360, 1],
			navigation: false,
			navigationText: ["<a class=\"flex-prev\"></a>", "<a class=\"flex-next\"></a>"],
			slideSpeed: 500,
			pagination: false,
			autoPlay: 6000

		});
	}
	
	if(jQuery('#brand-logo-slider').length > 0){
		
		jQuery("#brand-logo-slider .slider-items").owlCarousel({
			items: 6, //10 items above 1000px browser width
			itemsDesktop: [1024, 4], //5 items between 1024px and 901px
			itemsDesktopSmall: [900, 3], // 3 items betweem 900px and 601px
			itemsTablet: [600, 2], //2 items between 600 and 0;
			itemsMobile: [320, 1],
			navigation: false,
			navigationText: ["<a class=\"flex-prev\"></a>", "<a class=\"flex-next\"></a>"],
			slideSpeed: 500,
			pagination: false,
			autoPlay: 6000
		});
	}	
	
	if(jQuery('#category-desc-slider').length > 0){
		/* Category desc slider */
		jQuery("#category-desc-slider .slider-items").owlCarousel({
			autoPlay: true,
			items: 1, //10 items above 1000px browser width
			itemsDesktop: [1024, 1], //5 items between 1024px and 901px
			itemsDesktopSmall: [900, 1], // 3 items betweem 900px and 601px
			itemsTablet: [600, 1], //2 items between 600 and 0;
			itemsMobile: [320, 1],
			navigation: true,
			navigationText: ["<a class=\"flex-prev\"></a>", "<a class=\"flex-next\"></a>"],
			slideSpeed: 500,
			pagination: false
		});
	}
	
	if(jQuery('#related-products-slider').length > 0){
		/* Related products slider */
		jQuery("#related-products-slider .slider-items").owlCarousel({
			items: 4, //10 items above 1000px browser width
			itemsDesktop: [1024, 3], //5 items between 1024px and 901px
			itemsDesktopSmall: [980, 2], // 3 items betweem 900px and 601px
			itemsTablet: [768, 2], //2 items between 600 and 0;
			itemsMobile: [360, 1],
			navigation: false,
			navigationText: ["<a class=\"flex-prev\"></a>", "<a class=\"flex-next\"></a>"],
			slideSpeed: 500,
			pagination: true
		});
	}
	
	if(jQuery('#upsell-products-slider').length > 0){
		/* Upsell products slider */
		jQuery("#upsell-products-slider .slider-items").owlCarousel({
			items: 4, //10 items above 1000px browser width
			itemsDesktop: [1024, 3], //5 items between 1024px and 901px
			itemsDesktopSmall: [980, 2], // 3 items betweem 900px and 601px
			itemsTablet: [768, 2], //2 items between 600 and 0;
			itemsMobile: [360, 1],
			navigation: false,
			navigationText: ["<a class=\"flex-prev\"></a>", "<a class=\"flex-next\"></a>"],
			slideSpeed: 500,
			pagination: true
		});
	}

    jQuery('.J_filterToggle').on('click', function() {

        var div_id = jQuery(this).attr("data-id");
        jQuery('#'+div_id).toggleClass('filter-list-wrap-toggled');
    });

    jQuery('.slide_item').hover( function(){

        jQuery('.slide_item').css('width', '194px');
        jQuery('.slide_item').removeClass('active_slide');
        jQuery(this).css('width', '528px');
        jQuery(this).addClass('active_slide');
    });

	jQuery().UItoTop();
});


/*  UItoTop */
jQuery.fn.UItoTop = function(options) {
	var defaults = {
		text: '',
		min: 200,
		inDelay: 600,
		outDelay: 400,
		containerID: 'toTop',
		containerHoverID: 'toTopHover',
		scrollSpeed: 1200,
		easingType: 'linear'
	};
	var settings = jQuery.extend(defaults, options);
	var containerIDhash = '#' + settings.containerID;
	var containerHoverIDHash = '#' + settings.containerHoverID;
	jQuery('body').append('<a href="#" id="' + settings.containerID + '">' + settings.text + '</a>');
	jQuery(containerIDhash).hide().on("click", function() {
		jQuery('html, body').animate({
			scrollTop: 0
		}, settings.scrollSpeed, settings.easingType);
		jQuery('#' + settings.containerHoverID, this).stop().animate({
			'opacity': 0
		}, settings.inDelay, settings.easingType);
		return false;
	}).prepend('<span id="' + settings.containerHoverID + '"></span>').hover(function() {
		jQuery(containerHoverIDHash, this).stop().animate({
			'opacity': 1
		}, 600, 'linear');
	}, function() {
		jQuery(containerHoverIDHash, this).stop().animate({
			'opacity': 0
		}, 700, 'linear');
	});
	jQuery(window).scroll(function() {
		var sd = jQuery(window).scrollTop();
		if (typeof document.body.style.maxHeight === "undefined") {
			jQuery(containerIDhash).css({
				'position': 'absolute',
				'top': jQuery(window).scrollTop() + jQuery(window).height() - 50
			});
		}
		if (sd > settings.min) jQuery(containerIDhash).fadeIn(settings.inDelay);
		else jQuery(containerIDhash).fadeOut(settings.Outdelay);
	});
};

/* mobileMenu */
var isTouchDevice = "ontouchstart" in window || navigator.msMaxTouchPoints > 0;
jQuery.extend(jQuery.easing, {
        easeInCubic: function(e, t, n, i, s) {
            return i * (t /= s) * t * t + n
        },
        easeOutCubic: function(e, t, n, i, s) {
            return i * ((t = t / s - 1) * t * t + 1) + n
        }
    }),
    function(e) {
        e.fn.extend({
            accordion: function() {
                return this.each(function() {})
            }
        })
    }(jQuery)