//	Lupinia Studios
//	DeerSky Timer/Clock Operations
//	By Natasha L. 
//	www.lupinia.net | github.com/lupinia

// Clocks and Basic Operations
var first_run = true;	// Used to sync client time to server time

// Function: Use with setTimeout to increment all clocks once and initialize setInterval
// This allows for an arbitrary number of seconds in the first minute, to sync static HTML to real time
function load_updater() {
	if (first_run == true) {
		update_times();
		setInterval(update_times, 60 * 1000);
		first_run = false;
	}
}

// Function: Loop all clocks and increment by 1 minute every minute (setInterval payload)
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

// Function: Format an integer as a timestamp (H:mm or m:ss), returns a string
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

// ===============
// Timer Widget
var timer_start = 300;
var timer_cur = 0;
var timer_active = false;	// True if timer is running
var timer_open = false;		// True if timer widget is visible
var timer_started = false;	// True if timer has been started but not completed
var timer_handle;	// setInterval handle

// DOM elements
var timer_display;
var timer_obj;
var timer_container;
var timer_up_button;
var timer_down_button;
var timer_startstop_button;
var page_container;

// Function: Initialize timer variables
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

// Function: Set/update the timer's start value
function set_timer(t=timer_start) {
	if(timer_open && !timer_active && t > 0) {
		timer_cur = t;
		timer_display.innerHTML = format_time(timer_cur);
		if(!timer_started) {
			timer_start = t;
		}
	}
}

// Function: setInterval payload to subtract one second from the timer until it reaches zero
function step_timer() {
	if(timer_open && timer_active && timer_cur > 0) {
		timer_cur -= 1;
		if(timer_cur <= 0) {
			timer_cur = 0;
			stop_timer(true);
		}
		timer_display.innerHTML = format_time(timer_cur);
	}
}

// Function: Start the timer (initializes setInterval)
function start_timer() {
	if(timer_open && !timer_active) {
		timer_active = true;
		timer_handle = setInterval(step_timer, 1000);
		timer_display.classList.add("timer_running");
		set_button_state(timer_up_button, false);
		set_button_state(timer_down_button, false);
		timer_startstop_button.classList.add("timer_status_running");
		page_container.classList.remove("timer_complete");
	}
}

// Function: Stop the timer (timer_end == true if it has hit zero)
function stop_timer(timer_end=false) {
	if(timer_open && timer_active) {
		clearInterval(timer_handle);
		timer_active = false;
		timer_display.classList.remove("timer_running");
		if(timer_end) {
			timer_display.classList.add("timer_complete");
			page_container.classList.add("timer_complete");
			set_button_state(timer_startstop_button, false);
			timer_started = false;
		}
		else {
			set_button_state(timer_up_button, true);
			set_button_state(timer_down_button, true);
			page_container.classList.remove("timer_complete");
		}
		timer_startstop_button.classList.remove("timer_status_running");
	}
}

// Function: Enable or disable a specified timer button
function set_button_state(target_button, enable=true) {
	target_button.disabled = !enable;
	if(enable) {
		target_button.classList.remove("disabled");
	}
	else {
		target_button.classList.add("disabled");
	}
}

// Button: Show/hide timer widget
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
		if(timer_cur <= 0) {
			set_timer();
		}
		set_button_state(timer_up_button, true);
		set_button_state(timer_down_button, true);
		set_button_state(timer_startstop_button, true);
	}
	page_container.classList.remove("timer_complete");
}

// Button: Start or pause timer
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

// Button: Reset timer to last start value
function timer_reset_button() {
	if(timer_open) {
		if(timer_active) {
			stop_timer();
		}
		timer_display.classList.remove("timer_complete");
		set_button_state(timer_up_button, true);
		set_button_state(timer_down_button, true);
		set_button_state(timer_startstop_button, true);
		page_container.classList.remove("timer_complete");
		set_timer();
	}
}

// Button: Increase or decrease the start time for the timer
function change_timer(i=60) {
	if(timer_open && !timer_active && i) {
		set_timer(timer_cur+i);
	}
}
