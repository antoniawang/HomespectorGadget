// When any user clicks on a property's star
// Add the record to connect user and property in the UserProperty table
$(document).ready(function() {
	$("span.glyphicon-heart").click(function() {	//highlight the star
        console.log(this);
	  $(this).toggleClass("red");


// Send the new property to the database
    $.ajax("/add-favorites", {
    	method: "POST",
        datatype:"json",
    	data: {'property': $(this).attr("id")} 	// Nothing uses 'count'. Yet.
    	}).done(function() {
				console.log("Victory! Database contacted successfully");  		// confirm in the console
        });
    });
});


// When any user clicks on a property's "X"
// Delete this property from the session
$(document).ready(function() {
    $("span.glyphicon-pushpin").click(function() {    //highlight the star
        console.log(this);
      $(this).toggleClass("white");
      var that = this;
    // Send the new property to the database
    $.ajax("/delete-from-session", {
        method: "POST",
        datatype:"json",
        data: {'property': $(this).attr("id")}  // Nothing uses 'count'. Yet.
        }).done(function() {
                console.log(that.closest('tr'));
                that.closest('tr').remove();
                console.log("Victory! Database contacted successfully");        // confirm in the console
        });
    });
});                