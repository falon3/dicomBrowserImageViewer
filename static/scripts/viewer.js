Viewer = Backbone.View.extend({

    RADIUS: 2.5,
    SEGMENTS: 18,
    
    images: new Images(),
    mousePoint: {x: -1000, y: -1000},
    closeLine: null,
    closePoint: null,
    dragging: false,
    segments: this.SEGMENTS,
    naturalWidth: 1,
    natrualHeight: 1,
    scalingFactor: 1,
    slice: null,
    canvas: null,
    context: null,

    initialize: function(){
        _.each($("#preCachedImages img"), $.proxy(function(img, i){
            var image = new Image({src: $(img).attr('src')});
            this.images.add(image);
        }, this));
        this.slice = this.$("#slice");
        this.canvas = this.$("canvas")[0];
        this.context = this.canvas.getContext('2d');
        this.$("#curved").prop("checked", true);
        this.renderUI();
        this.render();
        
        /* Some event listeners */
        this.$("#canvas").bind('mousewheel DOMMouseScroll', $.proxy(this.scroll, this));
        $(window).bind('keyup', $.proxy(function(e){ if(e.keyCode == 46){ this.deletePoint(); }}, this)),
        $(window).resize($.proxy(this.render, this));
    },
    
    // Deletes the selected point
    deletePoint: function(){
        this.closeLine.getPoints().remove(this.closePoint);
        this.closePoint = null;
        this.render();
    },
    
    // Toggles whether or not to have curved lines
    changeSegments: function(){
        if(this.$("#curved").is(":checked")){
            this.segments = this.SEGMENTS;
        }
        else{
            this.segments = 1;
        }
        this.render();
    },
    
    // Display the previous image
    previous: function(e){
        this.images.previous();
        this.renderUI();
        this.render();
    },
    
    // Display the next image
    next: function(e){
        this.images.next();
        this.renderUI();
        this.render();
    },
    
    // Scroll forward/back the list of images
    scroll: function(e){
        if (e.originalEvent.wheelDelta > 0 || e.originalEvent.detail < 0) {
            // Go to the previous image
            if(!this.images.isFirst()){
                this.previous();
            }
        }
        else {
            // Go to the next image
            if(!this.images.isLast()){
                this.next();
            }
        }
        e.preventDefault();
    },
    
    // Toggles whether or not to go full screen
    toggleFullScreen: function(){
        this.$("#viewerContainer").toggleClass("fullscreen");
        if(this.$("#viewerContainer").hasClass("fullscreen")){
            this.$("#fullscreen img").attr("src", "/static/exitFullScreen.png");
            this.$("#fullscreen img").attr("alt", "Exit Full Screen");
            this.$("#fullscreen img").attr("title", "Exit Full Screen");
        }
        else{
            this.$("#fullscreen img").attr("src", "/static/fullScreen.png");
            this.$("#fullscreen img").attr("alt", "Full Screen");
            this.$("#fullscreen img").attr("title", "Full Screen");
        }
        this.render();
    },
    
    // Moving the mouse coordinates
    mouseMove: function(e){
        coords = this.canvas.relMouseCoords(e);
        coords.x *= this.scalingFactor;
        coords.y *= this.scalingFactor;
        this.mousePoint = coords;
        if(this.dragging){
            if(this.closeLine == null){
                this.closeLine = this.images.getCurrentImage().getCurrentLine();
            }
            this.closePoint.setCoords(this.mousePoint);
        }
        this.render();
    },
    
    // Clicking the mouse button (both left/right)
    mouseDown: function(e){
        coords = this.canvas.relMouseCoords(e);
        coords.x *= this.scalingFactor;
        coords.y *= this.scalingFactor;
        if(e.button == 2){
            // Right Click
            if(this.closePoint != null){
                this.deletePoint();
                return;
            }
            else {
                this.images.getCurrentImage().getLines().add(new Line());
            }
        }
        if(e.button == 0 || e.button == 2){
            // Left Click (or Right Click)
            this.dragging = true;
            if(this.closePoint == null){
                // Adding new point
                if(this.images.getCurrentImage().getCurrentLine() == null){
                    this.images.getCurrentImage().getLines().add(new Line());
                }
                this.closePoint = new Point({x: coords.x, y: coords.y});
                this.images.getCurrentImage().getCurrentLine().getPoints().add(this.closePoint);
            }
            else{
                this.images.getCurrentImage().setCurrentLine(this.closeLine);
            }
        }
        this.render();
    },
    
    // Leaving the canvas area
    mouseLeave: function(e){
        this.dragging = false;
        this.mousePoint = {x: -1000, y: -1000};
        this.render();
    },
    
    // Releasing the mouse button
    mouseUp: function(e){
        this.dragging = false;
        this.render();
    },
    
    events: {
        "click #previous": "previous",
        "click #next": "next",
        "change #curved": "changeSegments",
        "click #fullscreen a": "toggleFullScreen",
        "contextmenu #canvas": function(e){ e.preventDefault(); },
        "mousemove #canvas": "mouseMove",
        "mousedown #canvas": "mouseDown",
        "mouseleave #canvas": "mouseLeave",
        "mouseup #canvas": "mouseUp"
    },
    
    renderUI: function(){
        // Changing the image
        this.slice.attr("src", this.images.getCurrentImage().get('src'));
        this.$("#currentImage").text(this.images.currentId+1);
        this.$("#maxImage").text(this.images.length);
        
        // Updating button appearance
        if(this.images.isFirst()){
            this.$("#previous").prop('disabled', true);
        }
        else{
            this.$("#previous").prop('disabled', false);
        }
        if(this.images.isLast()){
            this.$("#next").prop('disabled', true);
        }
        else{
            this.$("#next").prop('disabled', false);
        }
    },

    render: function(){
        console.log("RENDER");
        if(this.slice[0] == undefined){
            // Something went wrong, try to re-get the slice
            this.slice = this.$("#slice");
        }
        this.naturalWidth = this.slice[0].naturalWidth;
        this.naturalHeight = this.slice[0].naturalHeight;
        
        this.scalingFactor = this.naturalWidth/this.slice.width();
        
        this.canvas.width = this.slice.width();
        this.canvas.height = this.slice.height();
        
        if(this.canvas.width == 0){
            // Image wasn't done loading yet, try again later...
            _.defer(this.render);
            return;
        }
        
        if(!this.dragging){
            this.closePoint = null;
            this.closeLine = null;
        }
        
        this.images.getCurrentImage().getLines().each(function(line, i){
            var curvePoints = new Array();
            line.getPoints().each(function(point, j){
                curvePoints.push(point.get('x')/this.scalingFactor);
                curvePoints.push(point.get('y')/this.scalingFactor);
                // While we are here, check distance to points
                if(!this.dragging && euclideanDistance(point.getCoords(), this.mousePoint) <= this.RADIUS*1.75){
                    this.closePoint = point;
                    this.closeLine = line;
                }
            }, this);
            
            this.context.drawCurve(curvePoints, 0.5, false, this.segments);
            this.context.strokeStyle = line.get('color');
            if(line == this.images.getCurrentImage().getCurrentLine()){
                this.context.lineWidth = 2/this.scalingFactor;
            }
            else{
                this.context.lineWidth = 1/this.scalingFactor;
            }
            this.context.stroke();
            line.getPoints().each(function(point, j){
                var radius = this.RADIUS/this.scalingFactor;
                if(point == this.closePoint && line == this.closeLine){
                    radius *= 1.75;
                }
                this.context.beginPath();
                this.context.arc(point.get('x')/this.scalingFactor, point.get('y')/this.scalingFactor, radius, 0, 2 * Math.PI, false);
                this.context.fillStyle = line.get('color');
                this.context.fill();
            }, this);
        }, this);
        
        this.context.beginPath();
        this.context.arc(this.mousePoint.x/this.scalingFactor, 
                         this.mousePoint.y/this.scalingFactor, 
                         this.RADIUS/this.scalingFactor, 0, 2 * Math.PI, false);
        this.context.fillStyle = 'red';
        this.context.fill();
    }

});

$(document).ready(function(){
    var viewer = new Viewer({el: $("#viewer")});
});
