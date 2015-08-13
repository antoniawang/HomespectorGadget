// When any user clicks on a property's star
// Add the record to connect user and property in the UserProperty table
$( document ).ready( function() {
	$( "p.species_span" ).click(function() {
	  $( this_property ).toggleClass("highlight");  				// mark the new bird