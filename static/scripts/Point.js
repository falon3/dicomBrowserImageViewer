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
    
    urlRoot: '/api/point',
    
    defaults: {
        x: 0,
        y: 0,
        line_id: null,
        interpolated: false
    }

});

Points = Backbone.Collection.extend({

    model: Point,
    
    set_id: '',
    
    study_id: '',
    
    url: function(){
        if(this.study_id == ''){
            return '/api/sessions/' + this.set_id + '/points';
        }
        else{
            return '/api/sessions/' + this.set_id + '/' + this.study_id + '/points';
        }
    }

});
