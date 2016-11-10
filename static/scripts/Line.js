Line = Backbone.Model.extend({

    initialize: function(){
        this.points = new Points();
    },
    
    getPoints: function(){
        return this.points;
    },
    
    urlRoot: '/api/line',
    
    defaults: {
        id: null,
        session_id: null,
        image_id: null,
        color: 'FF0000'
    }

});

Lines = Backbone.Collection.extend({

    initialize: function(){
        this.on("add", function(){
            this.setCurrentLine(this.last());
        }, this);
    },
    
    set_id: '',
    
    study_id: '',

    model: Line,
    
    currentLine: null,
    
    getCurrentLine: function(){
        return this.currentLine;
    },
    
    setCurrentLine: function(line){
        this.currentLine = line;
    },
    
    url: function(){
        if(this.study_id == ''){
            return '/api/sessions/' + this.set_id + '/lines';
        }
        else{
            return '/api/sessions/' + this.set_id + '/' + this.study_id + '/lines';
        }
    }

});
