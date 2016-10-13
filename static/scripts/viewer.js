$(document).ready(function(){

    var images = $("#preCachedImages img");
    var currentImage = 0;
    $("#viewer").attr("src", images[currentImage].src);
    $("#currentImage").text(currentImage+1);
    $("#maxImage").text(images.length);
    
    $("#viewer").bind('mousewheel DOMMouseScroll', function(e){
        if (e.originalEvent.wheelDelta > 0 || e.originalEvent.detail < 0) {
            currentImage = currentImage - 1;
        }
        else {
            currentImage = currentImage + 1;
        }
        currentImage = Math.min(images.length-1, Math.max(0, currentImage));
        $("#viewer").attr("src", images[currentImage].src);
        $("#currentImage").text(currentImage+1);
        e.preventDefault();
    });

});
