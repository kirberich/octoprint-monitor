var baseUrl = 'http://home.kirberich.uk:5000/api/';
var apiKey = 'nop';

var is_printing = false;
var current_temp = 0;
var target_temp = 0;
var job_name = '';
var estimated_time_total = 0;

toDuration = function (seconds) {
	var sec_num = parseInt(seconds, 10);
	var hours   = Math.floor(sec_num / 3600);
	var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
	var seconds = sec_num - (hours * 3600) - (minutes * 60);

	if (hours < 10) {
		hours   = "0" + hours;
	}
	if (minutes < 10) {
		minutes = "0" + minutes;
	}
	if (seconds < 10) {
		seconds = "0" + seconds;
	}

	return hours + ':' + minutes + ':' + seconds;
}

function update() {
	$.ajax({
		type: 'GET',
		url: baseUrl + 'printer',
		headers: {
			"X-Api-Key": apiKey,
	}}).done(function(data) {
		current_temp = data.temperature.tool0.actual;
		target_temp = data.temperature.tool0.target;
		is_printing = data.state.flags.printing;

		if (is_printing) {
			$(".state").text("Printing");
			$("main").removeClass("standby").addClass("printing");
		} else {
			$(".state").text("Standing By");
			$("main").addClass("standby").removeClass("printing");
		}

		$(".temp").text("Temperature: " + current_temp + '°' + " / " + target_temp + '°');
	});

	$.ajax({
		type: 'GET',
		url: baseUrl + 'job',
		headers: {
			"X-Api-Key": apiKey,
	}}).done(function(data) {
		job_name = data.job.file.name;
		estimated_time_total = data.job.estimatedPrintTime;
		time_elapsed = data.progress.printTime;
		estimated_time_remaining = data.progress.printTimeLeft;

		var progress_percent = data.progress.completion;
		$(".progress-indicator").css("width", progress_percent + "%");

		$(".job_name").text(job_name);
		$(".estimated_time_total").text("Estimated total: " + toDuration(estimated_time_total));
		$(".time_elapsed").text("Time elapsed: " + toDuration(time_elapsed));
		$(".estimated_time_remaining").text("Time remaining: " + toDuration(estimated_time_remaining));
	});
}

$(function() {
	setInterval(update, 500);
});
