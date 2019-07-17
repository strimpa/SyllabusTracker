

require.config({
	baseUrl: '/static/scripts/',
	paths: {
		jquery: 'lib/jquery-2.1.1',
		jqueryui: 'lib/jquery-ui.min',
		snap:'lib/snap.svg-min',
		sylvester:'lib/sylvester',
		jCookie:'lib/jquery.cookie',
		underscore:'lib/underscore-min',
		picker:'lib/jquery-plugins/picker.min',
		timepicker:'lib/jquery-plugins/jquery-ui-timepicker-addon'
	}
});

$ = require(
	['jquery', 'jqueryui'], function($, conn, ui)
{
	///////////////////////////////////////////////////////////////////////
	// globals
	///////////////////////////////////////////////////////////////////////
	// constants
	var max_depth = 1;
	//var csrftoken = $.cookie('csrftoken');
	// jquery extensions
	$.exists = function(selector){return ($(selector).length > 0);}

	///////////////////////////////////////////////////////////////////////
	// callbacks
	///////////////////////////////////////////////////////////////////////


	///////////////////////////////////////////////////////////////////////
	// startup triggers
	///////////////////////////////////////////////////////////////////////
	function csrfSafeMethod(method) {
		// these HTTP methods do not require CSRF protection
		return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}

	$.ajaxSetup();

	require(
		['picker'], function(picker)
	{
		// Setup of searchables
		$("select[multiple='']").picker({
			search:true
		})
	});

	$(".hover_icon").mouseover(function() {
		var formerPicUrl = $( this ).attr("src");
		var formerPic = formerPicUrl.split("/").pop().split(".")[0];
		$( this ).attr("src", "/static/images/"+formerPic+"_over.gif")
	}).mouseout(function() {
		var formerPicUrl = $( this ).attr("src");
		var formerPic = formerPicUrl.split("/").pop().split("_over")[0];
		$( this ).attr("src", "/static/images/"+formerPic+".gif")
	});

	$("#id_insurance_expiry_date").datepicker()
	require(['timepicker'], function(timepicker){
		$("#id_date").datetimepicker(
			//$.timepicker.regional['us']
			{
				dateFormat: 'yy-mm-dd', 
				timeFormat: 'HH:mm:ss',
				showTimezone: false,
				showSeconds:false
			}
		)
	});

	$(".rating").click(function(){this.children[0].checked = true});

	$("#filter_settings").accordion({
		collapsible:true,
		active:false,
		heightStyle:"content"
	});
	$("#filter_settings").click(function(){
		console.debug($(this));
		$(this).accordion( "refresh" );
	});

	///////////////////////////////////////////////////////////////////////////////////
	// Form watermark logic

	return $;
});