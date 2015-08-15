// When any user clicks on a property's star
// Add the record to connect user and property in the UserProperty table
$(document).ready(function() {
	$("span.glyphicon-star").click(function() {	//highlight the star
        console.log(this);
	  $(this).toggleClass("yellow");


// Send the new property to the database
    $.ajax("/add-favorites", {
    	method: "POST",
        datatype:"json",
    	data: {'property': $(this).attr("id")} 	// Nothing uses 'count'. Yet.
    	}).done(function() {
				console.log("Victory! Fave changed successfully");  		// confirm in the console
        });
    });
});


// When any user clicks on a property's "X"
// Delete this property from the session
$(document).ready(function() {
    $("span.glyphicon-pushpin").click(function() {    //highlight the star
        console.log(this);

      var that = this;
    // Send the new property to the database
    $.ajax("/delete-from-session", {
        method: "POST",
        datatype:"json",
        data: {'property': $(this).attr("id")}  // the remove class color doesn't work right now
        }).done(function() {
                $(this).removeClass("blue");
                $(this).addClass("white");
                alert(this)
                console.log(that.closest('tr'));
                setTimeout(function(){
                    that.closest('tr').remove();
                }, 2000);
                });
                console.log("Victory! Deleted from session.");        // confirm in the console
    });
}); 


//When property table loads, call ajax to update the lefthand column div
//Use the property-table app route to populate with properties from session
