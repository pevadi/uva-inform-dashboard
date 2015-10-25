{% load staticfiles %}
// Ensure jQuery is loaded
window.jQuery || document.write('<script src="//{{ request.get_host }}{% static "js/jquery-1.11.3.min.js" %}">\x3C/script>');

$.getScript("//{{ request.get_host }}{% url 'embed:ping_script' %}?{{ request.signed_url_params|safe }}")

if(document.location.pathname.match(/^\/lectures\//)){
	$.getScript("//{{ request.get_host }}{% url 'embed:video_script' %}?{{ request.signed_url_params|safe }}")
}

$.getScript("//{{ request.get_host }}{% url 'embed:dashboard_loader' %}?{{ request.signed_url_params|safe }}")
