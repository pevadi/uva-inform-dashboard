$(function(){
	var signed_params = "{{ request.signed_url_params|safe }}";
	var navbar = $(".navbar")
	var dashboard_container = $("<div>")
		.style("position", "fixed")
		.style("top", navbar.position().top + navbar.height())
		.style('background-color', 'white')
		.style('border', 'thin solid black')
		.style("width", "100%");

	var dashboard_iframe = $("iframe")
		//.attr("src", "//{{ request.get_host }}?"+signed_params)
		.attr("src", "//{{ request.get_host }}")
		.style('border':'0')
		.style('width': "100%")
		.style("height": "270px");

	dashboard_container.append(dashboard_iframe);

	var navbar_dropdown = $(".navbar-nav .dropdown");
	var dashboard_button = $("<li>")
		.style("padding", "8px 0px")
		.append($("<button class='btn btn-primary>").text("Dashboard"))
		.on("click", function(){ navbar.after(dashboard_container); })
	navbar_dropdown.before(dashboard_button);
})
