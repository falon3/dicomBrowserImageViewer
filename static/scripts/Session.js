Session = Backbone.Model.extend({

    initialize: function(){
        this.images = new Images();
    },
    
    setImages: function(images){
        this.images = images;
    },
    
    getImages: function(){
        return this.images;
    },
    
    urlRoot: '/api/session',
    
    defaults: function(){
        return {set_id: '',
                study_id: '',
                name: '',
                user_id: ''};
    }

});

Sessions = Backbone.Collection.extend({

    model: Session,
    
    url: function(){
        return '/api/sessions';
    }

});
