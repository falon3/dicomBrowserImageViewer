RADIUS = 3;

$(document).ready(function(){

    var images = $("#preCachedImages img");
    $("#curved").prop("checked", true);
    if(images.length == 0){
        return;
    }

    var points = new Array();
    var mousePoint = {x: 0, y: 0};
    var currentImage = 0;
    var closePointId = -1;
    var dragging = false;
    var segments = 16;
    
    var naturalWidth = 1;
    var naturalHeight = 1;
    
    var scalingFactor = 1;

    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    
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
        naturalWidth = $("#slice")[0].naturalWidth;
        naturalHeight = $("#slice")[0].naturalHeight;
        
        scalingFactor = naturalWidth/$("#slice").width();
        
        canvas.width = $("#slice").width();
        canvas.height = $("#slice").height();
        
        if(canvas.width == 0){
            // Image wasn't done loading yet, try again later...
            _.defer(render);
            return;
        }
        
        var curvePoints = new Array();
        if(!dragging){
            closePointId = -1;
        }
        _.each(points[currentImage], function(point, i){
            curvePoints.push(point.x/scalingFactor);
            curvePoints.push(point.y/scalingFactor);
            // While we are here, check distance to points
            if(!dragging && euclideanDistance(point, mousePoint) <= RADIUS*2/scalingFactor){
                closePointId = i;
            }
        });
        
        context.drawCurve(curvePoints, 0.5, false, segments);
        context.strokeStyle = 'red';
        context.lineWidth = 2/scalingFactor;
        context.stroke();
        _.each(points[currentImage], function(point, i){
            var radius = RADIUS/scalingFactor;
            if(i == closePointId){
                radius *= 2;
            }
            context.beginPath();
            context.arc(point.x/scalingFactor, point.y/scalingFactor, radius, 0, 2 * Math.PI, false);
            context.fillStyle = 'red';
            context.fill();
        });
        
        context.beginPath();
        context.arc(mousePoint.x/scalingFactor, mousePoint.y/scalingFactor, RADIUS/scalingFactor, 0, 2 * Math.PI, false);
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
    
    $(window).resize(render);
    
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
    
    $("#curved").change(function(e){
        if($("#curved").is(":checked")){
            segments = 16;
        }
        else{
            segments = 1;
        }
        render();
    });
    
    $("#fullscreen a").click(function(e){
        $("#viewerContainer").toggleClass("fullscreen");
        render();
    });
    
    // Mouse moving
    canvas.addEventListener('mousemove', function(e){
        coords = canvas.relMouseCoords(e);
        coords.x *= scalingFactor;
        coords.y *= scalingFactor;
        mousePoint = coords;
        if(dragging){
            points[currentImage][closePointId] = mousePoint;
        }
        render();
    });
    
    // Clicking to add a point
    canvas.addEventListener('mousedown', function(e){
        coords = canvas.relMouseCoords(e);
        coords.x *= scalingFactor;
        coords.y *= scalingFactor;
        dragging = true;
        if(closePointId != -1){
            
        }
        else{
            // Adding new point
            points[currentImage].push(coords);
            closePointId = points[currentImage].length - 1;
        }
        
        render();
    });
    
    // Leaving the canvas
    canvas.addEventListener('mouseleave', function(e){
        dragging = false;
        mousePoint = {x: -1000, y: -1000};
        render();
    });
    
    // Releasing the mouse
    canvas.addEventListener('mouseup', function(e){
        dragging = false;
        render();
    });

    render();

});
