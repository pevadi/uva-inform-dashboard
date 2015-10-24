{% load staticfiles %}

$.when(
	$.getScript("//{{ request.get_host }}{% static "js/ifvisible.min.js" %}"),
	$.getScript("//{{ request.get_host }}{% static "js/timeme.js" %}"),
    $.Deferred(function( deferred ){
        $( deferred.resolve );
    })
).done(function(){
	TimeMe.setIdleDurationInSeconds(60);
	TimeMe.setCurrentPageName(document.location.pathname);
	TimeMe.initialize();

	var signed_params = "{{ request.signed_url_params|safe }}";
	$(window).bind('beforeunload', function() {
	    $.post("//{{ request.get_host }}{% url 'storage:store_webpage_ping_event' %}?"+signed_params,{
			"location": document.location.href,
			"duration": TimeMe.getTimeOnCurrentPageInSeconds()
		});
	}
});
