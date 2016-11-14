Image = Backbone.Model.extend({

    initialize: function(){
        this.lines = new Lines();
    },
    
    setCurrentLine: function(line){
        this.getLines().setCurrentLine(line);
    },
    
    getCurrentLine: function(){
        return this.getLines().getCurrentLine();
    },
    
    getLines: function(){
        return this.lines;
    },

    urlRoot: '',
    
    defaults: {
        src: ''    
    }

});

Images = Backbone.Collection.extend({

    model: Image,

    currentId: 0,

    setCurrentId: function(currentId){
        this.currentId = Math.min(Math.max(currentId, 0), this.length-1);
    },

    // Returns the current image in the viewer
    getCurrentImage: function(){
        return this.at(this.currentId);
    },
    
    // Increments the counter and returns the next image
    next: function(){
        this.currentId = Math.min(this.currentId + 1, this.length-1);
        return this.getCurrentImage();
    },
    
    // Increments the counter and returns the next image
    previous: function(){
        this.currentId = Math.max(this.currentId - 1, 0);
        return this.getCurrentImage();
    },
    
    isFirst: function(){
        return (this.currentId == 0);
    },
    
    isLast: function(){
        return (this.currentId == this.length-1);
    },

    url: function(){
        return '';
    }

});
