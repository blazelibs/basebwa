WYMeditor.SKINS['pysapp'] = {

    init: function(wym) {

        //render following sections as panels
        jQuery(wym._box).find(wym._options.classesSelector)
          .prependTo("div.wym_area_top")
          .addClass("wym_dropdown")
          .find(WYMeditor.H2)
          .append("<span>&nbsp;&gt;</span>");

        //render following sections as buttons
        jQuery(wym._box).find(wym._options.toolsSelector)
          .addClass("wym_buttons");

        //render "Containers" and "Classes" as panels
        jQuery(wym._box).find(wym._options.containersSelector)
          .prependTo("div.wym_area_top")
          .addClass("wym_dropdown")
          .find(WYMeditor.H2)
          .append("<span>&nbsp;&gt;</span>");

        // auto add some margin to the main area sides if left area
        // or right area are not empty (if they contain sections)
        jQuery(wym._box).find("div.wym_area_right ul")
          .parents("div.wym_area_right").show()
          .parents(wym._options.boxSelector)
          .find("div.wym_area_main")
          .css({"margin-right": "155px"});

        jQuery(wym._box).find("div.wym_area_left ul")
          .parents("div.wym_area_left").show()
          .parents(wym._options.boxSelector)
          .find("div.wym_area_main")
          .css({"margin-left": "155px"});

        //make hover work under IE < 7
        jQuery(wym._box).find(".wym_section").hover(function(){
          jQuery(this).addClass("hover");
        },function(){
          jQuery(this).removeClass("hover");
        });
    }
};
