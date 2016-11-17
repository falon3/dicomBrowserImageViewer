Viewer = Backbone.View.extend({

    RADIUS: 2.5,
    SEGMENTS: 18,
    
    set_id: '',
    num_sessions: '',
    sessions: new Sessions(),
    currentSession: null,
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
        this.set_id = this.$el.attr("data-set_id");
        this.num_sessions = this.$el.attr("data-num_sessions");
        this.slice = this.$("#slice");
        this.canvas = this.$("canvas")[0];
        this.context = this.canvas.getContext('2d');
        this.$("#curved").prop("checked", true);
        this.$("#slider").val(0);
        
        this.render = _.debounce(this.render, 1);
        this.renderUI = _.debounce(this.renderUI, 1);
        
        this.init();
        
        /* Some event listeners */
        this.$("#canvas").bind('mousewheel DOMMouseScroll', $.proxy(this.scroll, this));
        $(window).bind('keyup', $.proxy(function(e){ if(e.keyCode == 46){ this.deletePoint(); }}, this)),
        $(window).resize($.proxy(this.render, this));
        $(window).mouseup($.proxy(this.mouseUp, this));
    },
    
    init: function(){
        var points = new Points();
        var lines = new Lines();
        points.set_id = this.set_id;
        lines.set_id = this.set_id;       
        this.sessions.set_id = this.set_id;
        pointsFetch = $.when(points.fetch());
        linesFetch = $.when(lines.fetch());
        sessionsFetch = $.when(this.sessions.fetch());
        
        pointsFetch.then(function(){
            return linesFetch;
        }).then(function(){
            lines.each(function(line){
                line.points.reset(points.where({line_id: line.get('id')}));
            });
            return sessionsFetch;
        }).then($.proxy(function(){
            this.sessions.each(function(session){
                var images = new Images();
                _.each(this.$("#preCachedImages img"), $.proxy(function(img, i){
                    var image = new Image({id: parseInt($(img).attr('data-id')), src: $(img).attr('src')});
                    image.lines.reset(lines.where({session_id: session.get('id'), image_id: image.get('id')}));
                    images.add(image);
                }, this));
                session.setImages(images);
            });
            if(this.sessions.length == 0){
                this.addSession();
            }
            this.currentSession = this.sessions.at(0);
            this.renderUI();
            this.render();
        }, this));
    },
    
    // Adding a new session
    addSession: function(){
        if(this.sessions.length < this.num_sessions){
            var session = new Session({set_id: this.set_id, name: 'Creating...'});
            var images = new Images();
            _.each(this.$("#preCachedImages img"), $.proxy(function(img, i){
                var image = new Image({id: parseInt($(img).attr('data-id')), src: $(img).attr('src')});
                images.add(image);
            }, this));
            session.setImages(images);
            session.save(null, {
                success: $.proxy(function(){
                    this.renderUI();
                    this.render();
                }, this)
            });
            this.sessions.add(session);
            this.currentSession = this.sessions.at(this.sessions.length-1);
        }
        this.renderUI();
        this.render();
    },
    
    // Deletes the selected point
    deletePoint: function(){
        var line = this.closeLine;
        this.closeLine.getPoints().remove(this.closePoint);
        this.closePoint.destroy({success: function(m){
            if(line.getPoints().length == 0){
                line.destroy();
            }
        }});
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
        this.currentSession.getImages().previous();
        this.renderUI();
        this.render();
    },
    
    // Display the next image
    next: function(e){
        this.currentSession.getImages().next();
        this.renderUI();
        this.render();
    },
    
    setImage: function(e){
        var val = this.$("#slider").val();
        this.currentSession.getImages().setCurrentId(val);
        this.renderUI();
        this.render();
    },
    
    // Scroll forward/back the list of images
    scroll: function(e){
        if (e.originalEvent.wheelDelta > 0 || e.originalEvent.detail < 0) {
            // Go to the previous image
            if(!this.currentSession.getImages().isFirst()){
                this.previous();
            }
        }
        else {
            // Go to the next image
            if(!this.currentSession.getImages().isLast()){
                this.next();
            }
        }
        e.preventDefault();
    },
    
    showSTL: function(){
        if($('#stl').is(":visible")){
            $('#stl').empty();
            $('#stl').hide();
        }
        else{
            $('#stl').show();
            init('/static/us_holder_pt2.stl', $('#stl'));
        }
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
    
    relMouseCoords: function(e){
        coords = this.canvas.relMouseCoords(e);
        coords.x *= this.scalingFactor;
        coords.y *= this.scalingFactor;
        coords.x = Math.min(Math.max(coords.x, this.RADIUS), this.naturalWidth-this.RADIUS);
        coords.y = Math.min(Math.max(coords.y, this.RADIUS), this.naturalHeight-this.RADIUS);
        return coords;
    },
    
    // Clicking on the session to display
    clickSession: function(e){
        var el = e.currentTarget;
        this.currentSession = this.sessions.findWhere({'name': $(el).text()});
        this.renderUI();
        this.render();
    },
    
    // Moving the mouse coordinates
    mouseMove: function(e){
        var coords = this.relMouseCoords(e);
        this.mousePoint = coords;
        if(this.dragging){
            if(this.closeLine == null){
                this.closeLine = this.currentSession.getImages().getCurrentImage().getCurrentLine();
            }
            this.closePoint.setCoords(this.mousePoint);
        }
        this.render();
    },
    
    // Clicking the mouse button (both left/right)
    mouseDown: function(e){
        var coords = this.relMouseCoords(e);
        var point = new Point({x: coords.x, y: coords.y});
        if(e.button == 2){
            // Right Click
            if(this.closePoint != null){
                this.deletePoint();
                return;
            }
            else {
                var line = new Line({session_id: this.currentSession.get('id'), image_id: this.currentSession.getImages().getCurrentImage().get('id')});
                line.save(null, {success:
                    function(){
                        line.points.each(function(p){
                            if(p.get('line_id') != line.get('id')){
                                p.set('line_id', line.get('id'));
                                p.save();
                            }
                        });
                    }
                });
                this.currentSession.getImages().getCurrentImage().getLines().add(line);
            }
        }
        if(e.button == 0 || e.button == 2){
            // Left Click (or Right Click)
            this.dragging = true;
            if(this.closePoint == null){
                // Adding new point
                if(this.currentSession.getImages().getCurrentImage().getCurrentLine() == null){
                    var line = new Line({session_id: this.currentSession.get('id'), image_id: this.currentSession.getImages().getCurrentImage().get('id')});
                    line.save(null, {success:
                        function(){
                            line.points.each(function(p){
                                if(p.get('line_id') != line.get('id')){
                                    p.set('line_id', line.get('id'));
                                    p.save();
                                }
                            });
                        }
                    });
                    this.currentSession.getImages().getCurrentImage().getLines().add(line);
                }
                else{
                    point.set('line_id', this.currentSession.getImages().getCurrentImage().getCurrentLine().get('id'));
                    if(e.button == 0 && !_.isNull(point.get('line_id'))){
                        point.save();
                    }
                }
                this.closePoint = point;
                this.currentSession.getImages().getCurrentImage().getCurrentLine().getPoints().add(this.closePoint);
            }
            else{
                this.currentSession.getImages().getCurrentImage().setCurrentLine(this.closeLine);
            }
        }
        this.render();
    },
    
    // Leaving the canvas area
    mouseLeave: function(e){
        if(!this.dragging){
            this.mousePoint = {x: -1000, y: -1000};
        }
        this.render();
    },
    
    // Releasing the mouse button
    mouseUp: function(e){
        if(this.closePoint != null && 
           !this.closePoint.isNew() &&
           !_.isNull(this.closePoint.get('line_id'))){
            this.closePoint.save();
        }
        this.dragging = false;
        this.mousePoint = {x: -1000, y: -1000};
        this.render();
    },
    
    events: {
        "click #previous": "previous",
        "click #next": "next",
        "input #slider": "setImage",
        "change #curved": "changeSegments",
        "click #showSTL": "showSTL",
        "click #fullscreen a": "toggleFullScreen",
        "click #sessions > div": "clickSession",
        "click #addSession": "addSession",
        "contextmenu #canvas": function(e){ e.preventDefault(); },
        "mousemove #canvas": "mouseMove",
        "mousedown #canvas": "mouseDown",
        "mouseleave #canvas": "mouseLeave",
    },
    
    renderUI: function(){
        // Changing the image
        this.slice.attr("src", this.currentSession.getImages().getCurrentImage().get('src'));
        this.$("#slider").val(this.currentSession.getImages().currentId);
        this.$("#currentImage").text(this.currentSession.getImages().currentId+1);
        this.$("#maxImage").text(this.currentSession.getImages().length);
        
        // Updating Add Session button
        if(this.sessions.length >= this.num_sessions){
            this.$("#addSession").prop('disabled', true);
        }
        else{
            this.$("#addSession").prop('disabled', false);
        }
        
        // Updating button appearance
        if(this.currentSession.getImages().isFirst()){
            this.$("#previous").prop('disabled', true);
        }
        else{
            this.$("#previous").prop('disabled', false);
        }
        if(this.currentSession.getImages().isLast()){
            this.$("#next").prop('disabled', true);
        }
        else{
            this.$("#next").prop('disabled', false);
        }
        this.$("#sessions").empty();
        this.sessions.each(function(session){
            var html = $("<div>" + session.get('name') + "</div>");
            if(session == this.currentSession){
                html.addClass('selected');
            }
            this.$("#sessions").append(html);
        }, this);
    },

    render: function(){
        this.naturalWidth = this.slice[0].naturalWidth;
        this.naturalHeight = this.slice[0].naturalHeight;
        
        this.scalingFactor = this.naturalWidth/this.slice.width();
        
        this.canvas.width = this.slice.width();
        this.canvas.height = this.slice.height();
        
        if(this.canvas.width == 0){
            // Image wasn't done loading yet, try again later...
            _.defer($.proxy(this.render, this));
            return;
        }
        
        if(!this.dragging){
            this.closePoint = null;
            this.closeLine = null;
            this.canvas.style.cursor = 'auto';
        }
        
        this.currentSession.getImages().getCurrentImage().getLines().each(function(line, i){
            var curvePoints = new Array();
            line.getPoints().each(function(point, j){
                curvePoints.push(point.get('x')/this.scalingFactor);
                curvePoints.push(point.get('y')/this.scalingFactor);
                // While we are here, check distance to points
                if(!this.dragging && euclideanDistance(point.getCoords(), this.mousePoint) <= this.RADIUS*1.75){
                    this.closePoint = point;
                    this.closeLine = line;
                    this.canvas.style.cursor = 'pointer';
                }
            }, this);
            
            this.context.drawCurve(curvePoints, 0.5, false, this.segments);
            this.context.strokeStyle = "#" + line.get('color');
            if(line == this.currentSession.getImages().getCurrentImage().getCurrentLine()){
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
                this.context.fillStyle = "#" + line.get('color');
                this.context.fill();
            }, this);
        }, this);
        
        /*this.context.beginPath();
        this.context.arc(this.mousePoint.x/this.scalingFactor, 
                         this.mousePoint.y/this.scalingFactor, 
                         this.RADIUS/this.scalingFactor, 0, 2 * Math.PI, false);
        this.context.fillStyle = 'red';
        this.context.fill();*/
    }

});

$(document).ready(function(){
    if($("#viewer").length > 0){
        var viewer = new Viewer({el: $("#viewer")});
    }
});
