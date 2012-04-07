var Tweet = Backbone.Model.extend({
});
var TweetView = Backbone.View.extend({
    className: 'tweet',
    render: function() {
        $(this.el).append(ich.tweet(this.model.toJSON()));
        return this;
    }
});
var TweetsAboutVideo = Backbone.Collection.extend({
    model: Tweet,
    initialize: function(models, options) {
        Backbone.Collection.prototype.initialize.call(this, models, options);
        this.vimeo_id = options.vimeo_id;
    },
    url: function() {
        return '/videos/' + this.vimeo_id + '/tweets/';
    }
});
var Video = Backbone.Model.extend({
    defaults: {
        'isSelected': false,
        'watched': false
    }
});
var VideoView = Backbone.View.extend({
    className: 'video',
    initialize: function() {
        this.model.on('deselected', this.deselect, this);
    },
    events: {
        'click .video_img': 'select',
        'click .watch_button': 'watch'
    },
    select: function() {
        var thisModel = this.model;
        document.videos.each(function(video) {
            if (video != thisModel)
                video.trigger('deselected');
        });
        $(this.videoDetails).empty();
        var selectedView = new VideoSelectedView({model: this.model});
        $(this.videoDetails).append(selectedView.el);
    },
    deselect: function() {
        $(this.videoDetails).empty();
        var deselectedView = new VideoDeselectedView({model: this.model});
        $(this.videoDetails).append(deselectedView.el);
    },
    watch: function() {
        document.videoPlayer.setModel(this.model);
    },
    render: function() {
        var renderedTemplate = ich.video(this.model.toJSON());
        $(this.el).append(renderedTemplate);
        this.videoDetails = $(this.el).find('.video_details')[0];
        this.deselect();
        return this;
    }
});
var VideoDeselectedView = Backbone.View.extend({
    className: 'deselected_video',
    initialize: function() {
        this.render();
    },
    render: function() {
        $(this.el).append(ich.video_title(this.model.toJSON()));
        return this;
    }
});
var VideoSelectedView = Backbone.View.extend({
    className: 'selected_video',
    initialize: function() {
        this.render();
    },
    render: function() {
        var attrs = this.model.toJSON();
        renderedTemplate = ich.video_details(attrs);
        $(this.el).append(renderedTemplate);

        var tweetsEl = $(this.el).find('.video_tweets');
        var tweets = new TweetsAboutVideo([], {vimeo_id: attrs.id});
        tweets.fetch();
        var tweetsView = new CollectionView(
            {memberViewClass: TweetView, collection: tweets, el: tweetsEl}
        );
        return this;
    }
});
var VideoPlayer = Backbone.View.extend({
    className: 'video_player',
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
        $(this.el).append(ich.selected_video(attrs));
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
    url: '/videos/',
});
var CollectionView = Backbone.View.extend({
    initialize: function() {
        this.memberViews = [];
        this.collection.bind('reset', this.render, this);
    },
    hideAllExcept: function(selectedId) {
    },
    render: function() {
        $(this.el).empty();
        var that = this;
        var viewClass = this.options.memberViewClass;
        this.collection.each(function(member) {
            that.memberViews.push(new viewClass({model : member}));
        });
        _(this.memberViews).each(function(memberView) {
            $(that.el).append(memberView.render().el);
        });
        return this;
    }
});

$(function() {
    // page only ever has one videos collection and one video player, hence the globals.
    document.videos = new Videos();
    document.videos.fetch();
    document.videosView = new CollectionView(
        {memberViewClass: VideoView, collection: document.videos, el: $('#videos')[0]}
    );
    document.videoPlayer = new VideoPlayer({el: $('#selected_video')[0]});
});
