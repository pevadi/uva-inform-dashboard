$(function(){
	var base_url = "{% if request.is_secure %}https{% else %}http{% endif %}://{{ request.get_host }}{% url 'get_zip' %}?{{ request.signed_url_params_unquoted|safe }}&f=";
	$("a").filter(function(index){
		var href = $(this).attr("href");
		if(href && href.match(/^http:\/\/cdn.mprog.nl\/prog-ai-new\/pset[0-9]+\.zip/)){
			$(this).attr('href', base_url+encodeURIComponent(href))
		}
	})
})
