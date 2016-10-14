$(document).ready(function(){

    var points = new Array();
    var mousePoint = {x: 0, y: 0};
    var images = $("#preCachedImages img");
    var currentImage = 0;
    
    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    
    if(images.length == 0){
        return;
    }
    
    // Initialize the points (this will probably be done via an api call eventually)
    _.each(images, function(img, i){
        points[i] = new Array();
    });
    
    // The main render function for the viewer.  
    // It is called everytime that a change has been made
    var render = function(){
        // Changing the image
        currentImage = Math.min(images.length-1, Math.max(0, currentImage));
        $("#slice").attr("src", images[currentImage].src);
        $("#currentImage").text(currentImage+1);
        $("#maxImage").text(images.length);
        
        // Canvas
        canvas.width = $("#slice").width();
        canvas.height = $("#slice").height();
        
        context.clearRect(0, 0, canvas.width, canvas.height);
        var curvePoints = new Array();
        _.each(points[currentImage], function(point){
            curvePoints.push(point.x);
            curvePoints.push(point.y);
        });
        
        context.drawCurve(curvePoints, 0.5, false, 16);
        context.strokeStyle = 'red';
        context.lineWidth = 2;
        context.stroke();
        _.each(points[currentImage], function(point, i){
            context.beginPath();
            context.arc(point.x, point.y, 3, 0, 2 * Math.PI, false);
            context.fillStyle = 'red';
            context.fill();
        });
        
        context.beginPath();
        context.arc(mousePoint.x, mousePoint.y, 3, 0, 2 * Math.PI, false);
        context.fillStyle = 'red';
        context.fill();
        
        // Updating button appearance
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
    
    // Clicking the Previous button
    $("#previous").click(function(){
        currentImage = currentImage - 1;
        render();
    });
    
    // Clicking the Next button
    $("#next").click(function(){
        currentImage = currentImage + 1;
        render();
    });
    
    // Mouse wheen scrolling
    $("#canvas").bind('mousewheel DOMMouseScroll', function(e){
        if (e.originalEvent.wheelDelta > 0 || e.originalEvent.detail < 0) {
            // Go to the previous image
            currentImage = currentImage - 1;
        }
        else {
            // Go to the next image
            currentImage = currentImage + 1;
        }
        
        render();
        e.preventDefault();
    });
    
    canvas.addEventListener('mousemove', function(e){
        coords = canvas.relMouseCoords(e);
        mousePoint = coords;
        render();
    });
    
    canvas.addEventListener('click', function(e){
        coords = canvas.relMouseCoords(e);
        points[currentImage].push(coords);
        render();
    });

    render();

});
