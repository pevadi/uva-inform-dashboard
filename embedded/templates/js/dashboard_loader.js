$(function(){
	var signed_params = "{{ request.signed_url_params_unquoted|safe }}";
	var navbar = $(".navbar");
	var dashboard_container = $("<div>")
		.attr("role", "dashboard")
		.addClass("hidden-xs hidden-sm")
		.css("position", "fixed")
		.css("top", navbar.position().top + navbar.height())
		.css('background-color', 'white')
		.css('border', 'thin solid black')
		.css("width", "100%")
		.css("z-index", "99")
		.css("display", "none");

	var dashboard_iframe = $("<iframe>")
		.attr("src", "//{{ request.get_host }}?"+signed_params)
		.css("border", "0")
		.css('width', "100%")
		.css("height", "340px");

	dashboard_container.append(dashboard_iframe);
	dashboard_container.append(
		$("<button type='button' class='close'>")
			.css("position", "fixed")
			.css("top", navbar.position().top + navbar.height()+10)
			.css("right", 10)
			.html("<span>&times;</span>")
			.on("click", function(){ dashboard_container.hide(); }));

	navbar.after(dashboard_container);

	var navbar_section = $(".navbar-nav.navbar-right");
	var dashboard_button = $("<li>")
		.addClass("hidden-xs hidden-sm")
		.css("padding", "8px 0px")
		.append(
			$("<button class='btn btn-primary'>")
				.on("click", function(){
					dashboard_container.toggle()
					if(dashboard_container.css("display") == "block"){
						$.post("//{{ request.get_host }}{% url 'storage:store_accessed_event' %}?{{ request.signed_url_params_unquoted|safe }}");
					}
				})
				.text("Dashboard"));
	navbar_section.prepend(dashboard_button);
});
