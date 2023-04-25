var view = "static"

var image_path = "..\\..\\static\\coins\\images\\"

var image_suffixes = [
    ["135", "90", "45"], 
    ["180", "top", "0"],  
    ["225", "270", "315"]];

// Temporary - fix later
var coin_name = "c5";

// Store original image:
var default_path = "";

// If the button is toggled, switch to interactive lighting
$('#coin_view_button').click(function (e) {
    console.log("click");

    var img = $('#coin-image');

    // Switch the view when the button is toggled
    if(view == "static") {
        // Enable interactive lighting and show the top down lighted image

        top_name = image_path + coin_name + "_obv_" + image_suffixes[1][1] + ".jpg";

        default_path = img.attr("src");

        img.attr("src", top_name);

        $('#image-toggle').text("Toggle Interactive Reverse")

        view = "obv";
    }
    else if(view == "obv") {
        // Switch to showing the reverse
        top_name = image_path + coin_name + "_rev_" + image_suffixes[1][1] + ".jpg";

        img.attr("src", top_name);

        $('#image-toggle').text("Toggle Default View")

        view = "rev";
    }
    else {
        // Switch back to the static image
        img.attr("src", default_path);
        view = "static";

        $('#image-toggle').text("Toggle Interactive Obverse");
    }


});

// Interactive lighting
$('#coin-image').click(function(e) {

    if(view == "obv" || view == "rev") {

        var img = $('#coin-image');

        // Get mouse position relative to the image
        var x = e.pageX - img.position().left;
        var y = e.pageY - img.position().top;

        // Select the image that is associated with the given region of the image
        var filename = image_path + coin_name + "_" + view + "_" +
        image_suffixes[Math.floor(y*3/img.height())][Math.floor(x*3/img.width())] + ".jpg";

        console.log(filename);

        // Change the image
        img.attr("src", filename);

    }

});