$( function() {
  $("#slider").slider({
    min: 2003,
    max: max_year,
    step: 1,
    range: true,
    values: [curr_min_year, curr_max_year],
    slide: function(event, ui) {
        for (var i = 0; i < ui.values.length; ++i) {
            $("input.sliderValue[data-index=" + i + "]").val(ui.values[i]);
          }
      }
  });

  $("input.sliderValue").change(function() {
    var $this = $(this);
    $("#slider").slider("values", $this.data("index"), $this.val());
  });

  $( "#petite" ).click(function( event ) {
     var year1 = document.getElementById("year1").value;
     var year2 = document.getElementById("year2").value;
     var error_count = 0
     if (!(year1 >= '2003' && year1 <= max_year)){error_count+=1}
     if (!(year2 >= '2003' && year2 <= max_year)){error_count+=1}
     if (error_count != 0){
       alert('Year(s) Entered Not Valid. Please Reenter Valid Numbers');
       event.preventDefault();
      }
     else{
       $("#year-submit").submit();
      }
    });
});
