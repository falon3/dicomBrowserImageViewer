$(document).ready(function(){

    var images = $("#preCachedImages img");
    var currentImage = 0;
    
    if(images.length == 0){
        return;
    }
    
    var render = function(){
        currentImage = Math.min(images.length-1, Math.max(0, currentImage));
        $("#viewer").attr("src", images[currentImage].src);
        $("#currentImage").text(currentImage+1);
        $("#maxImage").text(images.length);
        if(currentImage == 0){
            $("#previous").prop('disabled', true);
        }
        else{
            $("#previous").prop('disabled', false);
        }
        if(currentImage == images.length-1){
            $("#next").prop('disabled', true);
        }
        else{
            $("#next").prop('disabled', false);
        }
    }
    
    $("#previous").click(function(){
        currentImage = currentImage - 1;
        render();
    });
    
    $("#next").click(function(){
        currentImage = currentImage + 1;
        render();
    });
    
    $("#viewer").bind('mousewheel DOMMouseScroll', function(e){
        if (e.originalEvent.wheelDelta > 0 || e.originalEvent.detail < 0) {
            currentImage = currentImage - 1;
        }
        else {
            currentImage = currentImage + 1;
        }
        
        render();
        e.preventDefault();
    });

    render();

});
