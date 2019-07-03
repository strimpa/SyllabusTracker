

require.config({
	baseUrl: '/static/scripts/',
	paths: {
		jquery: 'lib/jquery-2.1.1',
		jqueryui: 'lib/jquery-ui.min',
		snap:'lib/snap.svg-min',
		sylvester:'lib/sylvester',
		jCookie:'lib/jquery.cookie',
		underscore:'lib/underscore-min',
        picker:'lib/jquery-plugins/picker.min'
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
		$( this ).attr("src", "/static/images/"+formerPic+"_over.png")
	}).mouseout(function() {
		var formerPicUrl = $( this ).attr("src");
		var formerPic = formerPicUrl.split("/").pop().split("_over")[0];
		$( this ).attr("src", "/static/images/"+formerPic+".png")
	});

	///////////////////////////////////////////////////////////////////////////////////
	// Form watermark logic

	return $;
});