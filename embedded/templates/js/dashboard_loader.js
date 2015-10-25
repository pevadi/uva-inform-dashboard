$(function(){
	var signed_params = "{{ request.signed_url_params|safe }}";
	var navbar = $(".navbar");
	var dashboard_container = $("<div>")
		.attr("role", "dashboard")
		.addClass("hidden-xs hidden-sm")
		.css("position", "fixed")
		.css("top", navbar.position().top + navbar.height())
		.css('background-color', 'white')
		.css('border', 'thin solid black')
		.css("width", "100%")
		.css("display", "none");

	var dashboard_iframe = $("<iframe>")
		//.attr("src", "//{{ request.get_host }}?"+signed_params)
		.attr("src", "//{{ request.get_host }}")
		.css("border", "0")
		.css('width', "100%")
		.css("height", "270px");

	dashboard_container.append(dashboard_iframe);
	dashboard_container.append(
		$("<button type='button' class='close'>")
			.css("position", "fixed")
			.css("top", navbar.position().top + navbar.height()+10)
			.css("right", 10)
			.html("<span>&times;</span>")
			.on("click", function(){ dashboard_container.hide(); }));

	navbar.after(dashboard_container);

	var navbar_dropdown = $(".navbar-nav .dropdown");
	var dashboard_button = $("<li>")
		.addClass("hidden-xs hidden-sm")
		.css("padding", "8px 0px")
		.append(
			$("<button class='btn btn-primary'>")
				.on("click", function(){
					dashboard_container.show()
				})
				.text("Dashboard"));
	navbar_dropdown.before(dashboard_button);
});
