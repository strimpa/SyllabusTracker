﻿

require.config({
	baseUrl: '/static/scripts/',
	paths: {
		jquery: 'lib/jquery-2.1.1',
		jqueryui: 'lib/jquery-ui.min',
		snap:'lib/snap.svg-min',
		sylvester:'lib/sylvester',
		jCookie:'lib/jquery.cookie',
		underscore:'lib/underscore-min',
		tagit:'lib/tag-it.min'
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
	var csrftoken = $.cookie('csrftoken');
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

	///////////////////////////////////////////////////////////////////////////////////
	// Form watermark logic

	return $;
});