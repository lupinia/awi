/* Lupinia Studios
 * DeerSky Timer/Clock Operations
 * By Natasha L. 
 * www.lupinia.net | github.com/lupinia
 * */
var first_run = true;
var timer_start = 300;
var timer_cur = 0;
var timer_active = false;
var timer_open = false;
var timer_started = false;
var timer_display;
var timer_obj;
var timer_container;
var timer_up_button;
var timer_down_button;
var timer_startstop_button;
var timer_handle;
var page_container;

function setup_timer() {
	timer_display = document.getElementById("timer_main_time");
	timer_obj = document.getElementById("timer_main");
	timer_container = document.getElementById("center_info");
	timer_up_button = document.getElementById("timer_adj_up");
	timer_down_button = document.getElementById("timer_adj_down");
	timer_startstop_button = document.getElementById("timer_start");
	page_container = document.getElementById("newtab");
	
	page_container.classList.add("has_timer");
	page_container.classList.remove("timer_complete");
}

function toggle_timer() {
	if(timer_open) {
		timer_container.classList.remove("timer_active");
		stop_timer();
		timer_display.classList.remove("timer_complete");
		timer_open = false;
	}
	else {
		timer_container.classList.add("timer_active");
		timer_open = true;
		if(!timer_cur) {
			set_timer();
		}
		timer_up_button.disabled = false;
		timer_down_button.disabled = false;
		timer_up_button.classList.remove("disabled");
		timer_down_button.classList.remove("disabled");
	}
	page_container.classList.remove("timer_complete");
}

function timer_startstop() {
	if(timer_open) {
		if(timer_active) {
			stop_timer();
		}
		else {
			start_timer();
			timer_started = true;
		}
	}
}

function timer_reset_button() {
	if(timer_open) {
		if(timer_active) {
			stop_timer();
		}
		timer_display.classList.remove("timer_complete");
		timer_up_button.disabled = false;
		timer_down_button.disabled = false;
		timer_up_button.classList.remove("disabled");
		timer_down_button.classList.remove("disabled");
		page_container.classList.remove("timer_complete");
		set_timer();
	}
}

function change_timer(i=60) {
	if(timer_open && !timer_active && i) {
		set_timer(timer_cur+i);
	}
}

function set_timer(t=timer_start) {
	if(timer_open && !timer_active && t) {
		timer_cur = t;
		timer_display.innerHTML = format_time(timer_cur);
		if(!timer_started) {
			timer_start = t;
		}
	}
}

function step_timer() {
	if(timer_open && timer_active && timer_cur) {
		timer_cur -= 1;
		if(!timer_cur) {
			stop_timer(true);
		}
		timer_display.innerHTML = format_time(timer_cur);
	}
}

function stop_timer(timer_end=false) {
	if(timer_open && timer_active) {
		clearInterval(timer_handle);
		timer_active = false;
		timer_display.classList.remove("timer_running");
		if(timer_end) {
			timer_display.classList.add("timer_complete");
			page_container.classList.add("timer_complete");
			timer_started = false;
		}
		else {
			timer_up_button.disabled = false;
			timer_down_button.disabled = false;
			timer_up_button.classList.remove("disabled");
			timer_down_button.classList.remove("disabled");
			page_container.classList.remove("timer_complete");
		}
		timer_startstop_button.classList.remove("timer_status_running");
	}
}

function start_timer() {
	if(timer_open && !timer_active) {
		timer_active = true;
		timer_handle = setInterval(step_timer, 1000);
		timer_display.classList.add("timer_running");
		timer_up_button.disabled = true;
		timer_down_button.disabled = true;
		timer_up_button.classList.add("disabled");
		timer_down_button.classList.add("disabled");
		timer_startstop_button.classList.add("timer_status_running");
		page_container.classList.remove("timer_complete");
	}
}

function format_time(t) {
	var minutes = 0;
	var seconds = 0;
	
	if(t > 59) {
		minutes = Math.floor(t / 60);
		//minutes = ((t % 60) + 60) % t;	// I hate this language so much
		seconds = t % 60;
	}
	else {
		seconds = t;
	}
	
	minutes = minutes.toString();
	seconds = seconds.toString();
	
	if(seconds.length < 2) {
		seconds = "0" + seconds;
	}
	
	return minutes + ":" + seconds;
}

function update_times() {
	var clocks = document.getElementsByClassName("timestamp_time");
	for (var i=0; i < clocks.length; i++) {
		var clock = clocks.item(i);
		var time = clock.innerHTML.split(":");
		var hours = parseInt(time[0]);
		var minutes = parseInt(time[1])+1;
		
		if (minutes > 59) {
			hours++;
			minutes = 0;
			
			if (hours > 23) {
				hours = 0;
			}
		}
		
		hours = hours.toString();
		minutes = minutes.toString();
		
		if (hours.length < 2) {
			hours = "0" + hours;
		}
		if (minutes.length < 2) {
			minutes = "0" + minutes;
		}
		
		clock.innerHTML = hours + ":" + minutes;
	}
}

function load_updater() {
	if (first_run == true) {
		update_times();
		setInterval(update_times, 60 * 1000);
		first_run = false;
	}
}
