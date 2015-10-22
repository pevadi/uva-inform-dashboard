{% load staticfiles %}
// Ensure jQuery is loaded
window.jQuery || document.write('<script src="//{{ request.get_host }}{% static "js/jquery-1.11.3.min.js" %}">\x3C/script>');

$(function(){
	$("<div>").addClass("alert alert-success alert-dismissible")
	.text("User {{ user }} has been successfully authenticated for the dashboard.")
	.append($("<button type='button' class='close' data-dismiss='alert'>×</button>"))
	.insertAfter(".navbar")
})

$.getScript("//{{ request.get_host }}{% url 'embed:ping_script' %}?{{ request.signed_url_params|safe }}")

if(document.location.pathname.match(/^\/lectures\//)){
	$.getScript("//{{ request.get_host }}{% url 'embed:video_script' %}?{{ request.signed_url_params|safe }}")
}
