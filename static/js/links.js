var Video = Backbone.Model.extend({
});

var VideoView = Backbone.View.extend({
    className: 'video',

    initialize: function() {
        this.model.bind('change', this.render, this);
    },

    events: {
        'click .video_img': 'selected'
    },

    selected: function() {
        document.selectedVideoView.setModel(this.model);
    },

    render: function() {
        var attrs = this.model.toJSON();
        renderedTemplate = ich.video_template(attrs);
        $(this.el).append(renderedTemplate);
        return this;
    }
});
var SelectedVideoView = Backbone.View.extend({
    className: 'selectedvideo',

    events: {
        'click .deselect_link': 'close',
        'click #overlay': 'close'
    },
    initialize: function() {
        _.bindAll(this, 'onKeypress');
        $(document).bind('keydown', this.onKeypress);
    },

    onKeypress: function(e) {
        if (e.keyCode === 27) this.close();
    },

    setModel: function(model) {
        this.model = model;
        this.render();
    },

    render: function() {
        var attrs = this.model.toJSON();
        $(this.el).append(ich.selected_video_template(attrs));
        $('#selected_video').show();
        return this;
    },

    close: function() {
        $(this.el).empty();
        $('#selected_video').hide();
    }
});
var Videos = Backbone.Collection.extend({
    model: Video,
    url: '/videos/'
});
var VideosView = Backbone.View.extend({
    initialize: function() {
        this.videoViews = [];
        this.collection.bind('reset', this.render, this);
    },

    render: function() {
        $(this.el).empty();
        var that = this;
        this.collection.each(function(video) {
            that.videoViews.push(new VideoView({model : video}));
        });
        _(this.videoViews).each(function(videoView) {
            $(that.el).append(videoView.render().el);
        });
        return this;
    }
});

$(function() {
    videos = new Videos();
    videos.fetch();
    var videosView = new VideosView({collection: videos, el: $('#videos')[0]});
    document.selectedVideoView = new SelectedVideoView({el: $('#selected_video')[0]});
});
