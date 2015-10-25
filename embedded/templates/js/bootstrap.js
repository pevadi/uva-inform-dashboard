{% load staticfiles %}
// Ensure jQuery is loaded
window.jQuery || document.write('<script src="//{{ request.get_host }}{% static "js/jquery-1.11.3.min.js" %}">\x3C/script>');

$.getScript("//{{ request.get_host }}{% url 'embed:ping_script' %}?{{ request.signed_url_params_unquoted|safe }}");

if(document.location.pathname.match(/^\/lectures\//)){
	$.getScript("//{{ request.get_host }}{% url 'embed:video_script' %}?{{ request.signed_url_params_unquoted|safe }}")
}

if(document.location.pathname.match(/^\/psets\//)){
	$.getScript("//{{ request.get_host }}{% url 'embed:pset_script' %}?{{ request.signed_url_params_unquoted|safe }}");
}

$.get("//{{ request.get_host }}{% url 'has_treatment' %}?{{ request.signed_url_params_unquoted|safe }}", function(has_treatment){
	if(has_treatment) $.getScript("//{{ request.get_host }}{% url 'embed:dashboard_loader' %}?{{ request.signed_url_params_unquoted|safe }}");
});
