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
});
var VideoView = Backbone.View.extend({
    className: 'video',
    initialize: function() {
        // the VideoView has several subsidiary, modal views
        this.detailsView = new VideoDetailsView({model: this.model});
        this.tweetsView = new TweetsAboutVideoView({model: this.model});
        this.deselectedView = new VideoDeselectedView({model: this.model});
        // start in deselected state
        this.model.trigger('deselected');
    },
    events: {
        'click .video_details_link': 'select',
        'click .watch_video_link': 'watch'
    },
    select: function() {
        var toDeselect = this.model.collection.without(this.model);
        _(toDeselect).each(function(video) {
            video.trigger('deselected');
        });
        this.model.trigger('selected');
    },
    watch: function() {
        window.videoPlayer.setModel(this.model);
    },
    render: function() {
        $(this.el).empty();
        var renderedTemplate = ich.video(this.model.toJSON());
        $(this.el).append(renderedTemplate);

        this.$watchButton = $(this.$('.watch_video_link')[0]);
        var $videoDetails = $(this.$('.video_details')[0]);
        $videoDetails.append(this.deselectedView.el, this.detailsView.el,
                this.tweetsView.el);
        return this;
    }
});
var ModalView = Backbone.View.extend({
    xStart: 0,
    xFinish: 230,
    initialize: function() {
        this.render();
        this.model.on('deselected', this.deselect, this);
        this.model.on('selected', this.select, this);
    },
    select: function() {
        $(this.el).css({left: this.xStart}).show().animate({left: this.xFinish});
    },
    deselect: function() {
        $(this.el).hide();
    }
});
var VideoDetailsView = ModalView.extend({
    className: 'selected_video',
    render: function() {
        $(this.el).append(ich.video_details(this.model.toJSON()));
        return this;
    }
});
var VideoDeselectedView = ModalView.extend({
    className: 'deselected_video',
    select: function() {
        $(this.el).fadeOut();
    },
    deselect: function() {
        $(this.el).fadeIn();
    },
    render: function() {
        $(this.el).append(ich.video_title(this.model.toJSON()));
        return this;
    }
});
var TweetsAboutVideoView = ModalView.extend({
    xFinish: 510,
    className: 'video_tweets',
    initialize: function() {
        this.tweets = new TweetsAboutVideo([], {vimeo_id: this.model.get('id')});
        this.tweets.bind('reset', this.render, this);
        ModalView.prototype.initialize.call(this);
    },
    select: function() {
        if (!this.tweets.length)
            this.tweets.fetch();
        ModalView.prototype.select.call(this);
    },
    render: function() {
        $(this.el).empty();
        if (this.tweets.length)
            this.tweets.each(function(tweet) {
                $(this.el).append(new TweetView({model: tweet}).render().el);
            }.bind(this));
        else
            this.$el.text("We haven't recorded any tweets about this video");
        return this;
    }
});
var VideoPlayer = Backbone.View.extend({
    events: {
        'click .deselect_link': 'close',
        'click #overlay': 'close'
    },
    initialize: function() {
        _.bindAll(this, 'onKeypress');
        $(window).bind('keydown', this.onKeypress);
    },
    onKeypress: function(e) {
        if (e.keyCode === 27) this.close();
    },
    setModel: function(model) {
        this.model = model;
        this.render();
    },
    render: function() {
        $(this.el).append(ich.video_player(this.model.toJSON()));
        return this;
    },
    close: function() {
        $(this.el).empty();
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
        this.collection.fetch();
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
    window.videosView = new CollectionView(
        {memberViewClass: VideoView, collection: new Videos(), el: $('#videos')[0]}
    );
    window.videoPlayer = new VideoPlayer({el: $('#selected_video')[0]});
});
