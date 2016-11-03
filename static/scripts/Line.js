Line = Backbone.Model.extend({

    initialize: function(){
        this.points = new Points();
    },
    
    getPoints: function(){
        return this.points;
    },
    
    urlRoot: '',
    
    defaults: {
        id: null,
        session_id: null,
        image_id: null,
        color: '#FF0000'
    }

});

Lines = Backbone.Collection.extend({

    initialize: function(){
        this.on("add", function(){
            this.setCurrentLine(this.last());
        }, this);
    },

    model: Line,
    
    currentLine: null,
    
    getCurrentLine: function(){
        return this.currentLine;
    },
    
    setCurrentLine: function(line){
        this.currentLine = line;
    },
    
    url: function(){
        return '';
    }

});
