$(function(){
	$("a").filter(function(index){
		var href = $(this).attr("href");
		if(href && href.match(/^http:\/\/cdn.mprog.nl\/prog-ai\/pset[0-9]+\.zip/)){
			$(this).attr('href', "{{ request.get_host }}{% url 'get_zip' %}?{{ request.signed_url_params|safe }}&f="+encodeURIComponent(href))
		}
	})
})
