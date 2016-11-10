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
                study_id: 1,
                name: '',
                user_id: '',
                color: 'FF0000'};
    }

});

Sessions = Backbone.Collection.extend({

    model: Session,
    
    set_id: '',
    
    study_id: '',
    
    url: function(){
        if(this.study_id == ''){
            return '/api/sessions/' + this.set_id;
        }
        else{
            return '/api/sessions/' + this.set_id + '/' + this.study_id;
        }
    }

});
