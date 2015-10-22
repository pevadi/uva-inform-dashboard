var ytvideos = [];

YTVideo = function(videoId, height, width, containerId){
	var _this = this;
	var timeoutInterval = 10000;

	_this.player = null; // Placeholder for YT player
	_this.timer = null; // Placeholder for setTimeOut timer

	_this.initialize = function(){
		_this.player = new YT.Player(containerId, {
			height: height,
			width: width,
			videoId: videoId,
			playerVars: {"modestbranding": 1 },
			events: {
				'onReady': _this.onPlayerReady,
				'onStateChange': _this.onPlayerStateChange
			}
		})
	};

	_this.onPlayerReady = function(event){
		_this.debug("video is ready.")
	};

	_this.showDebug = false;
	_this.debug = function(message){
		if(_this.showDebug && window.console && console.log){
			console.log("["+videoId+"] "+message);
		}
	};

	_this.onPlayerStateChange = function(event){
		_this.debug("video state changed.")
		var current_time = event.target.getCurrentTime();
		if (event.data == YT.PlayerState.PLAYING) {
			if(_this.timer) clearTimeout(_this.timer); _this.timer = null;
			_this.last_time_tic = current_time;
			_this.timer = setTimeout(_this.onTimeWatched, timeoutInterval);
		}else if(event.data == YT.PlayerState.PAUSED ||
				event.data == YT.PlayerState.BUFFERING ||
				event.data == YT.PlayerState.ENDED){
			if(_this.timer) clearTimeout(_this.timer); _this.timer = null;
		}
	}

	_this.onTimeWatched = function(){
		if(_this.timer && _this.player){
			var current_time = _this.player.getCurrentTime();
			var secondsWatched = (current_time - _this.last_time_tic);
			_this.debug("Counting seconds: "+ secondsWatched);
			_this.last_time_tic = current_time;
			_this.timer = setTimeout(_this.onTimeWatched, timeoutInterval);
	        $.ajax("//{{ request.get_host }}{% url 'store_event' %}?{{ request.signed_url_params|safe }}",{
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    "verb":"http://adlnet.gov/expapi/verbs/experienced",
                    "object": {
                        "id": _this.player.getVideoUrl(),
                        "objectType": "Activity",
                        "definition": {
                            "type": "http://adlnet.gov/expapi/activities/media"
                        }
                    },
                    "result": {
                        "duration": "PT"+Math.round(secondsWatched*100)/100+"S"
                    },
                    "timestamp": new Date().toISOString()
                })
            });
		}
	}
}

$(function(){
	$.getScript("https://www.youtube.com/iframe_api");
	$("iframe").each(function(){
		var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*/;
		var match = $(this).attr("src").match(regExp);
		if (match && match[7].length==11){
			var containerId = "ytplayer"+Object.keys(ytvideos).length;
			ytvideos.push(new YTVideo(match[7], $(this).attr("height"),
						$(this).attr("width"), containerId));
			$(this).replaceWith($("<div>").attr("id", containerId));
		}
	});
});

function onYouTubeIframeAPIReady() {
	for(var i = 0; i < ytvideos.length; i++){
		ytvideos[i].initialize()
	}
}
