// When any user clicks on a property's star
// Add the record to connect user and property in the UserProperty table
$( document ).ready( function() {
	$( "button.favorite-star" ).click(function() {	//highlight the star
	  $( this_property ).toggleClass("highlight");



// Send the new bird to the database
    $.ajax("/add_favorites", {
    	method: "POST",
        datatype:"json",
    	data: {'property': $(this_property).attr("id")} 	// Nothing uses 'count'. Yet.
    	}).done(function() {
				console.log("Victory! Database contacted successfully");  		// confirm in the console
		});
  })};