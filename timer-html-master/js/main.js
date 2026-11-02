(function($){
    $.fn.scrollingTo = function( opts ) {
        var defaults = {
            animationTime : 1000,
            easing : '',
            callbackBeforeTransition : function(){},
            callbackAfterTransition : function(){}
        };

        var config = $.extend( {}, defaults, opts );

        $(this).click(function(e){
            var eventVal = e;
            e.preventDefault();

            var $section = $(document).find( $(this).data('section') );
            if ( $section.length < 1 ) {
                return false;
            };

            if ( $('html, body').is(':animated') ) {
                $('html, body').stop( true, true );
            };

            var scrollPos = $section.offset().top;

            if ( $(window).scrollTop() == scrollPos ) {
                return false;
            };

            config.callbackBeforeTransition(eventVal, $section);

            $('html, body').animate({
                'scrollTop' : (scrollPos+'px' )
            }, config.animationTime, config.easing, function(){
                config.callbackAfterTransition(eventVal, $section);
            });
        });
    };

    /* Contact form submits to configured API only; no fake success before deployment. */
    const form = document.getElementById("contact-form");
    if (form) {
        form.addEventListener("submit", async function(event) {
            event.preventDefault();
            const status = document.getElementById("contact-status");
            const submit = document.getElementById("contact-submit");
            const directMail = "mailto:info@786solution.com";
            const endpoint = (form.getAttribute("data-api-url") || "").trim();
            const safeMessage = function(message, error) {
                status.hidden = false;
                status.className = "contact-status " + (error ? "is-error" : "is-success");
                status.textContent = message;
            };
            if (!form.reportValidity()) return;
            if (!endpoint || !/^https:\/\/[^\/\s]+\/[^?\s]+$/i.test(endpoint)) {
                status.hidden = false;
                status.className = "contact-status";
                status.textContent = "Online submission is not configured yet. Please contact us directly: ";
                const link = document.createElement("a");
                link.href = directMail;
                link.textContent = "Email 786 Solution";
                status.appendChild(link);
                return;
            }
            const data = {
                name: form.elements.name.value.trim(),
                email: form.elements.email.value.trim(),
                phone: form.elements.phone.value.trim(),
                subject: form.elements.subject.value.trim(),
                message: form.elements.message.value.trim(),
                website: form.elements.website.value.trim()
            };
            submit.disabled = true;
            safeMessage("Sending your message...", false);
            try {
                const timeout = new AbortController();
                const timer = setTimeout(function(){ timeout.abort(); }, 20000);
                let response;
                try {
                    response = await fetch(endpoint, {
                        method: "POST",
                        mode: "cors",
                        credentials: "omit",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(data),
                        signal: timeout.signal
                    });
                } finally { clearTimeout(timer); }
                const body = await response.json().catch(function(){ return {}; });
                if (response.ok && body.ok === true) {
                    safeMessage("Your message was sent successfully. Thank you!", false);
                    form.reset();
                } else {
                    safeMessage("Message could not be sent. Please email info@786solution.com directly.", true);
                }
            } catch (error) {
                safeMessage("Could not reach our contact service. Please email info@786solution.com directly.", true);
            } finally { submit.disabled = false; }
        });
    }

}(jQuery));



jQuery(document).ready(function(){
	"use strict";
	new WOW().init();


(function(){
 jQuery('.smooth-scroll').scrollingTo();
}());

});




$(document).ready(function(){

    $(window).scroll(function () {
        if ($(window).scrollTop() > 50) {
            $(".navbar-brand a").css("color","#fff");
            $("#top-bar").removeClass("animated-header");
        } else {
            $(".navbar-brand a").css("color","inherit");
            $("#top-bar").addClass("animated-header");
        }
    });

    $("#clients-logo").owlCarousel({
 
        itemsCustom : false,
        pagination : false,
        items : 5,
        autoplay: true,

    });


});



// fancybox
$(".fancybox").fancybox({
    padding: 0,

    openEffect : 'elastic',
    openSpeed  : 450,

    closeEffect : 'elastic',
    closeSpeed  : 350,

    closeClick : true,
    helpers : {
        title : { 
            type: 'inside' 
        },
        overlay : {
            css : {
                'background' : 'rgba(0,0,0,0.8)'
            }
        }
    }
});






 




