

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
	['jquery', 'jqueryui', 'picker'], function($, conn, ui, picker)
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

	// Setup of searchables
    $("select").picker({
		search:true
	})
	$("span.pc-trigger").text("Search ...")


	///////////////////////////////////////////////////////////////////////////////////
	// Form watermark logic

	return $;
});