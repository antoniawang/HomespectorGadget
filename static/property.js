//HOMEPAGE
$(document).ready(function() {
    $(this).load(function(){
        $.ajax("/homepage").done(function(result) {
            $('#contents').html(result);
        });
    });
});


//LOGIN
//Makde modal appear
$(document).ready(function() {
    $("#login").click(function(){
    //show login form
        $.get("/login", "login-form.html").done(function(results) {
            console.log("Got" + results);
            var contents = results;
            $("#login-form").html(contents);
            console.log("Make div appear!"); 
            // confirm in the console
            $("#login-form").css("display","block");
        });
    });
});    

//Make the login window disapear after submission
//in the login-form.html script


//SEARCH
//When user searches an address
//Pass the text contents to the search app route
//Make the modal appear
$(document).ready(function() {
    $.ajax("/property-list").done(function(result) {
        $("#left-col").html(result);
    }); 
    $("#search-btn").click(function() {
        console.log("Search!");

// Send the new property to the database
        $.get("/search", {'address-search': $("#address-search").val()}).done(function(results) {
        // {
        // method: "GET",
        // datatype:"json",
        // data: {'address_search': $("#address-search").val()} 
        // }).get(function(results) {
            console.log("Got" + results);
            var contents = results;
            $("#address-confirm").html(contents);
            console.log("Make div appear!");    // confirm in the console
            $("#address-confirm").css("display","block");
           
        });
    });
});


//Make the address confimation window disapear when user clicks "No"
$(document).ready(function() {
    $("#confirm-no").click(function() {
        console.log("Make div disappear!");
        $("#address-confirm").css("display","none");
        $.post("/delete-property", {'Delete-Property': $(this).attr("id")});
        console.log("Deleted from session");
    });
});

