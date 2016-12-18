
function Plotter(container){
	var _this = this;

	var listeners = {};
	_this.on = function(event_name, callback){
		if(event_name in listeners){
			listeners[event_name].push(callback);
		}else{
			listeners[event_name] = [callback];
		}
	};
	_this.trigger = function(event_name, data){
		if( !(event_name in listeners) ) return;
		for(var i = 0; i < listeners[event_name].length; i++){
			listeners[event_name][i].call(_this, data);
		}
	}

	_this.get_container_width = function(){
		return $(container).width();
	};

	_this.get_container_height = function(){
		return $(container).height();
	};

	_this.initialize = function(){};
	_this.draw = function(){};
	_this.load_data = function(){};
	_this.clear_canvas = function(){
		$(container).empty();
	};

	var axis_label = "hoeveelheid";
	_this.set_axis_label = function(axis){ axis_label = axis };
	_this.get_axis_label = function(){ return axis_label };

	_this.show_no_data_message = function(msg){
		if(msg == undefined) msg = "Er zijn nog geen resultaten beschikbaar";
		_this.clear_canvas();
		$(container).append($("<div>")
			.addClass("no-data-message")
			.text(msg));
	};

	_this.show_loading_message = function(msg){
		if(msg == undefined) msg = "Resultaten worden geladen...";
		_this.clear_canvas();
		$(container).append($("<div>")
			.addClass("no-data-message")
			.text(msg));
		$(container).append($("<div>")
			.addClass("loader"));
	};
}

function RadarPlotter(container){

	var _parent = new Plotter(container);
	var _this = $.extend(this, _parent);

	var margin, width, height;
	var chart;

	_this.initialize = function(){
		margin = { top: 10, right: 10, bottom: 20, left: 10 };
		width = _this.get_container_width() - margin.left - margin.right;
		height = _this.get_container_height() - margin.top - margin.bottom;
	};

	_this.draw = function(){
		_this.clear_canvas();

		chart = d3.select(container).append("svg")
            .attr("width", width +margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
           .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	};

	_this.load_data = function(data){
		if(data){
            var chart = RadarChart.chart();
            RadarChart.defaultConfig.radius = 3;
			RadarChart.defaultConfig.w = width;
			RadarChart.defaultConfig.h = height;
			RadarChart.defaultConfig.maxValue = 1;
			radar_ready_data = [];
			var var_names = data['variable_names'];
			var student_statistics = data['student_statistics'];
			var mean_statistics = data['mean_statistics'];

			if(var_names.length == 2){
				RadarChart.defaultConfig.radius = 6;
			}


			// Student data
			studentSeries = {className:'student', axes:[]};
			for( var i = 0 ; i < student_statistics.length; i++){
				studentSeries['axes'][i] = {axis:var_names[i], value:student_statistics[i]};
			}
			radar_ready_data[0] = studentSeries;

			// Students mean data
			studentsMeanSeries = {className:'Other students', axes:[]};
			for( var i = 0 ; i < mean_statistics.length; i++){
				studentsMeanSeries['axes'][i] = {axis:var_names[i], value:mean_statistics[i]};
			}
			radar_ready_data[1] = studentsMeanSeries;
			console.log(studentSeries);

			RadarChart.draw(container, radar_ready_data);

		}else{
			_this.show_no_data_message("Deze studieresultaten zijn nog niet beschikbaar");
		}
	};
}

function PiePlotter(container){
	var _parent = new Plotter(container);
	var _this = $.extend(this, _parent);

	var margin, width, height, radius;
	var chart, pie, color, arc;

	_this.initialize = function(){

		margin = { top: 20, right: 20, bottom: 40, left: 50 };
		width = _this.get_container_width() - margin.left - margin.right;
		height = _this.get_container_height() - margin.top - margin.bottom;
        radius = Math.min(width, height) / 2;

        color = d3.scale.ordinal()
                .range(["red", "green"]);

        arc = d3.svg.arc()
                .outerRadius(radius - 10)
                    .innerRadius(0);

        pie = d3.layout.pie()
                .sort(null)
                    .value(function(d) { return d; });

	};

	_this.draw = function(){
		_this.clear_canvas();

        chart = d3.select(container).append("svg")
            .attr("width", width)
            .attr("height", height)
          .append("g")
            .attr("transform", "translate(" + (width-40) / 2 + "," + height / 2 + ")");

	};

	_this.load_data = function(data){
		if( data && 'mean' in data){
            data = [1-data['mean'], data['mean']];
            var g = chart.selectAll(".arc")
              .data(pie(data))
            .enter().append("g")
              .attr("class", "arc");

            g.append("path")
              .attr("d", arc)
              .style("fill", function(d,i) { return color(i); });

            var legend = chart.append("g")
              .attr("class", "legend")
              .attr("width", radius)
              .attr("height", radius * 2)
              .selectAll("g")
              .data(data)
              .enter().append("g")
              .attr("transform", function(d, i) { return "translate("+radius+"," + i * 20 + ")"; });

            legend.append("rect")
              .attr("width", 18)
              .attr("height", 18)
              .style("fill", function(d, i) { return color(i); });

            legend.append("text")
              .attr("x", 24)
              .attr("y", 9)
              .attr("dy", ".35em")
              .text(function(d, i) { return (i?"Geslaagd":"Niet geslaagd"); });

		}else{
			_this.show_no_data_message("Deze studieresultaten zijn nog niet beschikbaar");
		}
	};
}


function GaussPlotter(container){
	var _parent = new Plotter(container);
	var _this = $.extend(this, _parent);

	var margin, width, height;
	var x, y, xAxis, yAxis;
	var line;
	var chart, curve;

	_this.initialize = function(){

		margin = { top: 20, right: 20, bottom: 40, left: 50 };
		width = _this.get_container_width() - margin.left - margin.right;
		height = _this.get_container_height() - margin.top - margin.bottom;

		// Defining the range of the x axis
		x = d3.scale.linear()
			.range([0, width])
			.domain([0,10]);

		// Defining the range of the y axis
		y = d3.scale.linear()
			.range([height, 0])
			.domain([0,1]);

		// Defining the x axis
		xAxis = d3.svg.axis()
			.scale(x)
			.orient("bottom")
			.ticks(10);

		// Defining the y axis
		yAxis = d3.svg.axis()
			.scale(y)
			.orient("left")
			.ticks(10, "%");

		// Defining the line function
		line = d3.svg.line()
			.x(function(d) {
				return x(d.x);
			})
			.y(function(d) {
				return y(d.y);
			});
	};

	_this.draw = function(){
		_this.clear_canvas();
		chart = d3.select(container).append("svg")
			.attr("width", width + margin.left + margin.right)
			.attr("height", height + margin.top + margin.bottom)
			.append("g")
			.attr("transform",
				"translate(" + margin.left + "," + margin.top + ")");

		chart.append("g")
			.attr("class", "x axis lined")
			.attr("transform", "translate(0," + height + ")")
			.call(xAxis)
			.append("text")
			.style("text-anchor", "end")
			.attr("x", width-10)
			.attr("y", 30)
			.text(_this.get_axis_label());

		chart.append("g")
			.attr("class", "y axis")
			.call(yAxis)
			.append("text")
			.attr("transform", "rotate(-90)")
			.attr("y", -50)
			.attr("dy", ".71em")
			.style("text-anchor", "end")
			.text("probability");

		curve = chart.append("path")
			.datum([]) // todo?
			.attr("class", "line")
			.attr("d", line);
	};

	_this.load_data = function(data){
		if( data && 'mean' in data && 'variance' in data){
			var mean = data['mean']
			var variance = data['variance']
			variance += 0.2;
			var distribution = gaussian(mean, variance);
			data = [];
			for(var i = 0; i < 10; i += 0.05){
				data.push({'x': i, 'y': distribution.pdf(i)});
			}
			curve.transition().attr("d", line(data));
		}else{
			_this.show_no_data_message("Deze studieresultaten zijn nog niet beschikbaar");
		}
	}
}


function BarPlotter(container){
	var _parent = new Plotter(container);
	var _this = $.extend(this, _parent);

	var margin, width, height, sliderHeight, sliderMargin, sliderPadding;
	var x, y, xAxis, yAxis;
	var line;
	var chart, bar;
	var handle, brush;

	_this.initialize = function(){
		margin = {top: 20, right: 20, bottom: 40, left: 50};
		width = _this.get_container_width() - margin.left - margin.right;
		height = _this.get_container_height() - margin.top - margin.bottom;

		sliderHeight = 20, sliderMargin = 5, sliderPadding = 3;
		plotHeight = height - sliderHeight - sliderMargin;

		// Defining the range for the x axis
		x = d3.scale.ordinal()
			.rangeBands([0, width], 0.1);

		// Defining the range for the y axis
		y = d3.scale.linear()
			.range([plotHeight, 0]);

		// Define the x axis
		xAxis = d3.svg.axis()
			.scale(x)
			.orient("bottom");

		// Define the y axis
		yAxis = d3.svg.axis()
			.scale(y)
			.orient("left")
			.ticks(5, "%");

		brush = d3.svg.brush()
			.x(x)
			.extent([0, 0])
			.on("brush", brushed);

		function brushed() {
			var value = brush.extent()[0];
			if (d3.event.sourceEvent) { // not a programmatic event
				var coord = d3.mouse(this)[0];
				var distances = x.range().map(function(r,i){
					return Math.abs(r + (x.rangeBand()/2) - coord);
				});
				var i = distances.indexOf(Math.min.apply(Math,distances));
				value = x.domain()[i];
				_this.select_active("g[data-label='"+value+"']");
				brush.extent([value, value]);
			}
			if(x(""+value)){
				_this.select_active("g[data-label='"+value+"']");
			}
		}
	};

	_this.draw = function(){
		_this.clear_canvas();

		chart = d3.select(container).append("svg")
			.attr("width", width +margin.left + margin.right)
			.attr("height", height + margin.top + margin.bottom)
		   .append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	};

	_this.select_active = function(selector){
		d3.select('.bargroup.active').classed("active",false)
		d3.select(selector).classed("active", true)
		handle.attr("x", x(d3.select(selector).attr("data-label")));
		_this.trigger('select-bin', d3.select(selector).attr("data-bin"));
	}

	_this.load_data = function(data){
        var student_bin = data['student_bin'];
        var data = data['bins'];

		var total_count = 0;

		data.forEach(function(d, i){
			total_count += d['count'];
		});

		data.forEach(function(d, i){
			d['label'] = Math.round(10*(d.lower+d.upper)/2)/10;
			d.count = d.count / total_count
		});

		x.domain(data.map(function(d) { return d.label }));
		y.domain(d3.extent(data, function(d) { return d.count; }));

		bar = chart.selectAll("g")
			.data(data)
		  .enter().append("g")
            .attr("class", "bargroup")
			.attr("data-label", function(d){ return d.label })
			.attr("data-bin", function(d){ return d.id })
			.on("click", function(){ _this.select_active(this) })
			.attr("transform", function(d, i) {
				return "translate(" + x(d.label) + ",0)"; });

		bar.append("rect")
			.attr("class", "bar")
			.attr("y", function(d){ return y(d.count) })
			.attr("height", function(d){ return plotHeight-y(d.count) })
			.attr("width", x.rangeBand());

		chart.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height + ")")
			.call(xAxis)
			.append("text")
			.style("text-anchor", "end")
			.attr("x", width-10)
			.attr("y", sliderHeight+10)
			.text(_this.get_axis_label());

		chart.append("g")
			.attr("class", "y axis")
			.call(yAxis)
			.append("text")
			.attr("transform", "rotate(-90)")
			.attr("y", -50)
			.attr("dy", ".71em")
			.style("text-anchor", "end")
			.text("# students");

		var slider = chart.append("g")
			.attr("class", "slider")
			.call(brush);

		slider.selectAll(".extent,.resize")
			.remove();

		slider.select(".background")
			.style("visibility", "visible")
			.style("cursor", "pointer")
			.attr("y", height-sliderHeight)
			.attr("height", sliderHeight);

		handle = slider.append("rect")
			.attr("class", "handle")
			.attr("y", height-sliderHeight+sliderPadding)
			.attr("width",  x.rangeBand())
			.attr("height", sliderHeight-(2*sliderPadding));

		if(student_bin>-1){
			console.log("student bin found")
			_this.select_active("g[data-bin='"+student_bin+"']");
			var student_bar = d3.select("g[data-bin='"+student_bin+"']")
				.classed("bar-you", true)
				.append("text")
				.style("font-size", (40/30)*x.rangeBand()+"px")
				.style("font-weight", "bold")
				.attr("y", function(d){ return y(d.count)+
					(plotHeight-y(d.count) < 50 ?
						(-1/30)*x.rangeBand(): (35/30)*x.rangeBand()
					)
				})
				.attr("x", (8/30)*x.rangeBand())
				.text("*");
		}

		// _this.select_active("g[data-bin='"+student_bin+"']");
	}
}


