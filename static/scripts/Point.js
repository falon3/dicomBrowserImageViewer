Point = Backbone.Model.extend({

    initialize: function(){
    
    },
    
    setCoords: function(coords){
        this.set('x', coords.x);
        this.set('y', coords.y);
    },
    
    getCoords: function(){
        return {x: this.get('x'),
                y: this.get('y')};
    },
    
    urlRoot: '',
    
    defaults: {
        x: 0,
        y: 0,
        interpolated: false
    }

});

Points = Backbone.Collection.extend({

    model: Point,
    
    url: function(){
        return '';
    }

});
