// Debug function
jQuery.fn.debug = function() {
  return this.each(function(){
    console.dir(this);
  });
};

// Default function to handle jQuery Ajax failures:
jQuery.HandleAjaxError = function( xhr, errorString, exception ) {
    if( xhr.status == '404' ) {
        alert('Ajax Request Failed: ' + xhr.status + ' requested page not found');
    } else {
        alert('Ajax Request Failed: ' + xhr.status + ' ' + 'status response received' );
    }
};

// Default Ajax Settings
jQuery.ajaxSetup({
    // timeout is 5 seconds
    timeout: 5000,
    // the function that gets called if there is an HTTP Request Error or an error
    // in one of the functions that is being called after the request is done
    error: jQuery.HandleAjaxError,
    // Expect JSON datatype
    dataType: "json"
});
