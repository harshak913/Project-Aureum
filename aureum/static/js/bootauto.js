$( function() {
    var availableTags = companies;
    $( "#tags" ).autocomplete({
      source: availableTags
    });
  } );
