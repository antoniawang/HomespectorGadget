//VIEW STATE
PageState = {
    TABLE : 0,
    MAP: 1,
    INDEX: 2
};

var viewState = PageState.INDEX;


//HOMEPAGE
$(document).ready(function() {
    $(this).load(function(){
        viewState = PageState.INDEX;
        $.ajax("/homepage").done(function(result) {
            $('#contents').html(result);
        });
    });
});


//LOGIN
//Make login modal appear
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
            $.ajax("/property-list").done(function(result) {
                $("#left-col").html(result);
            }); 
        });
    });
});    

//REGISTER
//Makde register modal appear
$(document).ready(function() {
    $("#register").click(function(){
    //show registration form
        $.get("/register", "registration-form.html").done(function(results) {
            console.log("Got" + results);
            var contents = results;
            $("#login-form").html(contents);
            console.log("Make div appear!"); 
            // confirm in the console
            $("#login-form").css("display","block");
            $(".modal-login").css("height","100%");
        });
    });
});    


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
            console.log("Got" + results);
            var contents = results;
            $("#address-confirm").html(contents);
            console.log("Make div appear!");    // confirm in the console
            $("#address-confirm").css("display","block");
        });   
    });
});


//Switch to map view
$(document).ready(function() {
    $("#map-view-select").click(function() {

        console.log("Make map appear!");
        viewState = PageState.MAP;
        $.ajax("/default-map").done(function(result) {
            $("#contents").html(result);
            $("span.glyphicon-check").css("display","none");
            $("span.glyphicon-map-marker").css("display", "inline");
            $("span.glyphicon-certificate").css("display", "inline");
            $("span.glyphicon-home").css("display", "inline");
            console.log(viewState);
        }); 
    });
});

//Switch to table view
$(document).ready(function() {
    $("#table-view-select").click(function() {
        console.log("Make table appear!");
        viewState = PageState.TABLE;
        $.ajax("/comparison-table").done(function(result) {
            $("#contents").html(result);
            $("span.glyphicon-check").css("display","inline");
            $("span.glyphicon-map-marker").css("display", "none");
            $("span.glyphicon-certificate").css("display", "none");
            $("span.glyphicon-home").css("display", "none");
        }); 
    });
});

