/*
 * WYMeditor : what you see is What You Mean web-based editor
 * Copyright (c) 2008 Jean-Francois Hovinne, http://www.wymeditor.org/
 * Dual licensed under the MIT (MIT-license.txt)
 * and GPL (GPL-license.txt) licenses.
 *
 * For further information visit:
 *        http://www.wymeditor.org/
 *
 * File Name:
 *        jquery.wymeditor.resizable.js
 *        resize plugin for WYMeditor
 *
 * File Authors:
 *        Peter Eschler (peschler _at_ gmail.com)
 *
 * Version:
 *        0.3
 *
 * Changelog:
 *
 * 0.3
 *     - Added 'iframeOriginalSize' and removed 'ui.instance' calls (jfh).
 *
 * 0.2
 *     - Added full support for all jQueryUI resizable plugin options.
 *     - Refactored and documented code.
 * 0.1
 *     - Initial release.
 */

/**
 * The resizable plugin makes the wymeditor box vertically resizable.
 * It it based on the ui.resizable.js plugin of the jQuery UI library.
 *
 * The WYMeditor resizable plugin supports all parameters of the jQueryUI
 * resizable plugin. The parameters are passed like this:
 *
 *         wym.resizable({ handles: "s,e",
 *                         maxHeight: 600 });
 *
 * @param options options for the plugin  
 */
WYMeditor.editor.prototype.resizablec = function(options) {
  
    var wym = this;
    var iframe = jQuery(wym._box).find('iframe');
    var iframeOriginalSize = {};

    // Define some default options
    var default_options = {
        start: function(e, ui) {               
            iframeOriginalSize = {
                width: jQuery(iframe).width(),
                height: jQuery(iframe).height()
            }
        },

        // resize is called by the jQuery resizable plugin whenever the
        // client area was resized.
        resize: function(e, ui) {                
            var diff = ui.size.height - ui.originalSize.height;
            jQuery(iframe).height( iframeOriginalSize.height + diff );

            // If the plugin has horizontal resizing disabled we need to
            // adjust the "width" attribute of the area css, because the
            // resizing will set a fixed width (which breaks liquid layout
            // of the wymeditor area).
            if( !ui.options.handles['w'] && !ui.options.handles['e'] ) {
                ui.size.width = "inherit";
            }
        },
        handles: "s,e,se",
        minHeight: 250,
        maxHeight: 600
    };

    // Merge given options with default options. Given options override
    // default ones.
    var final_options = jQuery.extend(default_options, options);

    jQuery(wym._box).resizable(final_options);

};
