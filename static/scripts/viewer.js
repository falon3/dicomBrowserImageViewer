RADIUS = 2.5;

$(document).ready(function(){

    var images = $("#preCachedImages img");
    $("#curved").prop("checked", true);
    if(images.length == 0){
        return;
    }

    var points = new Array();
    var mousePoint = {x: 0, y: 0};
    var currentImage = 0;
    var currentLine = new Array();
    var closePointId = -1;
    var closeLineId = -1;
    var dragging = false;
    var segments = 18;
    
    var naturalWidth = 1;
    var naturalHeight = 1;
    
    var scalingFactor = 1;

    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    
    // Initialize the points (this will probably be done via an api call eventually)
    _.each(images, function(img, i){
        points[i] = new Array();
    });
    
    var deleteSelectedPoint = function(){
        points[currentImage][closeLineId].splice(closePointId, 1);
        closePointId = -1;
        render();
    };
    
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
        
        if(!dragging){
            closePointId = -1;
            closeLineId = -1;
        }
        
        _.each(points[currentImage], function(line, i){
            var curvePoints = new Array();
            _.each(line, function(point, j){
                curvePoints.push(point.x/scalingFactor);
                curvePoints.push(point.y/scalingFactor);
                // While we are here, check distance to points
                if(!dragging && euclideanDistance(point, mousePoint) <= RADIUS*1.75){
                    closePointId = j;
                    closeLineId = i;
                }
            });
            
            context.drawCurve(curvePoints, 0.5, false, segments);
            context.strokeStyle = 'red';
            if(i == currentLine[currentImage]){
                context.lineWidth = 2/scalingFactor;
            }
            else{
                context.lineWidth = 1/scalingFactor;
            }
            context.stroke();
            _.each(line, function(point, j){
                var radius = RADIUS/scalingFactor;
                if(j == closePointId && i == closeLineId){
                    radius *= 1.75;
                }
                context.beginPath();
                context.arc(point.x/scalingFactor, point.y/scalingFactor, radius, 0, 2 * Math.PI, false);
                context.fillStyle = 'red';
                context.fill();
            });
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
    };
    
    /* Event Listeners */
    
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
    
    // Clicking the curved button
    $("#curved").change(function(e){
        if($("#curved").is(":checked")){
            segments = 18;
        }
        else{
            segments = 1;
        }
        render();
    });
    
    // Clicking the full screen button
    $("#fullscreen a").click(function(e){
        $("#viewerContainer").toggleClass("fullscreen");
        if($("#viewerContainer").hasClass("fullscreen")){
            $("#fullscreen img").attr("src", "/static/exitFullScreen.png");
            $("#fullscreen img").attr("alt", "Exit Full Screen");
            $("#fullscreen img").attr("title", "Exit Full Screen");
        }
        else{
            $("#fullscreen img").attr("src", "/static/fullScreen.png");
            $("#fullscreen img").attr("alt", "Full Screen");
            $("#fullscreen img").attr("title", "Full Screen");
        }
        render();
    });
    
    // Pressing the delete key
    $(window).keyup(function(e){
        if(e.keyCode == 46){ // Delete
            deleteSelectedPoint();
        }
    });
    
    // Disable the context menu
    canvas.addEventListener('contextmenu', function(e){
        e.preventDefault();
    });
    
    // Mouse moving
    canvas.addEventListener('mousemove', function(e){
        coords = canvas.relMouseCoords(e);
        coords.x *= scalingFactor;
        coords.y *= scalingFactor;
        mousePoint = coords;
        if(dragging){
            if(closeLineId == -1){
                closeLineId = currentLine[currentImage];
            }
            points[currentImage][closeLineId][closePointId] = mousePoint;
        }
        render();
    });
    
    // Clicking to add a point
    canvas.addEventListener('mousedown', function(e){
        coords = canvas.relMouseCoords(e);
        coords.x *= scalingFactor;
        coords.y *= scalingFactor;
        if(e.button == 2){
            // Right Click
            if(closePointId != -1){
                deleteSelectedPoint();
                return;
            }
            else {
                currentLine[currentImage] = points[currentImage].length;
            }
        }
        if(e.button == 0 || e.button == 2){
            // Left Click (or Right Click)
            dragging = true;
            if(closePointId == -1){
                // Adding new point
                if(currentLine[currentImage] == undefined){
                    currentLine[currentImage] = 0;
                }
                if(points[currentImage][currentLine[currentImage]] == undefined){
                    points[currentImage][currentLine[currentImage]] = new Array();
                }
                points[currentImage][currentLine[currentImage]].push(coords);
                closePointId = points[currentImage][currentLine[currentImage]].length - 1;
            }
            else{
                currentLine[currentImage] = closeLineId;
            }
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
