RADIUS = 2.5;

$(document).ready(function(){

    $("#curved").prop("checked", true);
    if($("#preCachedImages img").length == 0){
        return;
    }

    var images = new Images();
    var mousePoint = {x: 0, y: 0};
    var closePoint = null;
    var closeLine = null;
    var dragging = false;
    var segments = 18;
    
    var naturalWidth = 1;
    var naturalHeight = 1;
    
    var scalingFactor = 1;

    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    
    // Initialize the points (this will probably be done via an api call eventually)
    _.each($("#preCachedImages img"), function(img, i){
        var image = new Image({src: $(img).attr('src')});
        images.add(image);
    });
    
    var deleteSelectedPoint = function(){
        closeLine.getPoints().remove(closePoint);
        closePoint = null;
        render();
    };
    
    // The main render function for the viewer.  
    // It is called everytime that a change has been made
    var render = function(){
        // Changing the image
        $("#slice").attr("src", images.getCurrentImage().get('src'));
        $("#currentImage").text(images.currentId+1);
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
            closePoint = null;
            closeLine = null;
        }
        
        images.getCurrentImage().getLines().each(function(line, i){
            var curvePoints = new Array();
            line.getPoints().each(function(point, j){
                curvePoints.push(point.get('x')/scalingFactor);
                curvePoints.push(point.get('y')/scalingFactor);
                // While we are here, check distance to points
                if(!dragging && euclideanDistance(point.getCoords(), mousePoint) <= RADIUS*1.75){
                    closePoint = point;
                    closeLine = line;
                }
            });
            
            context.drawCurve(curvePoints, 0.5, false, segments);
            context.strokeStyle = 'red';
            if(line == images.getCurrentImage().getCurrentLine()){
                context.lineWidth = 2/scalingFactor;
            }
            else{
                context.lineWidth = 1/scalingFactor;
            }
            context.stroke();
            line.getPoints().each(function(point, j){
                var radius = RADIUS/scalingFactor;
                if(point == closePoint && line == closeLine){
                    radius *= 1.75;
                }
                context.beginPath();
                context.arc(point.get('x')/scalingFactor, point.get('y')/scalingFactor, radius, 0, 2 * Math.PI, false);
                context.fillStyle = 'red';
                context.fill();
            });
        });
        
        context.beginPath();
        context.arc(mousePoint.x/scalingFactor, mousePoint.y/scalingFactor, RADIUS/scalingFactor, 0, 2 * Math.PI, false);
        context.fillStyle = 'red';
        context.fill();
        
        // Updating button appearance
        if(images.isFirst()){
            $("#previous").prop('disabled', true);
        }
        else{
            $("#previous").prop('disabled', false);
        }
        if(images.isLast()){
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
        images.previous();
        render();
    });
    
    // Clicking the Next button
    $("#next").click(function(){
        images.next();
        render();
    });
    
    // Mouse wheen scrolling
    $("#canvas").bind('mousewheel DOMMouseScroll', function(e){
        if (e.originalEvent.wheelDelta > 0 || e.originalEvent.detail < 0) {
            // Go to the previous image
            if(!images.isFirst()){
                images.previous();
                render();
            }
        }
        else {
            // Go to the next image
            if(!images.isLast()){
                images.next();
                render();
            }
        }
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
            if(closeLine == null){
                closeLine = images.getCurrentImage().getCurrentLine();
            }
            closePoint.setCoords(mousePoint);
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
            if(closePoint != null){
                deleteSelectedPoint();
                return;
            }
            else {
                images.getCurrentImage().getLines().add(new Line());
            }
        }
        if(e.button == 0 || e.button == 2){
            // Left Click (or Right Click)
            dragging = true;
            if(closePoint == null){
                // Adding new point
                if(images.getCurrentImage().getCurrentLine() == null){
                    images.getCurrentImage().getLines().add(new Line());
                }
                closePoint = new Point({x: coords.x, y: coords.y});
                images.getCurrentImage().getCurrentLine().getPoints().add(closePoint);
            }
            else{
                images.getCurrentImage().setCurrentLine(closeLine);
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
