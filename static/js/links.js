var Tweet = Backbone.Model.extend({
});
var TweetView = Backbone.View.extend({
    className: 'tweet',
    render: function() {
        $(this.el).append(ich.tweet_template(this.model.toJSON()));
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
        this.model.bind('change', this.render, this);
    },
    events: {
        'click .video_img': 'selected',
        'click .tweets': 'display_tweets'
    },
    selected: function() {
        document.selectedVideoView.setModel(this.model);
    },
    display_tweets: function(e) {
        var attrs = this.model.toJSON();
        tweets = new TweetsAboutVideo([], {vimeo_id: attrs.id});
        tweets.fetch();
        var tweetsView = new CollectionView(
            {memberViewClass: TweetView, collection: tweets, el: e.target}
        );
    },
    render: function() {
        renderedTemplate = ich.video_template(this.model.toJSON());
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
var CollectionView = Backbone.View.extend({
    initialize: function() {
        this.memberViews = [];
        this.collection.bind('reset', this.render, this);
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
    videos = new Videos();
    videos.fetch();
    var videosView = new CollectionView(
        {memberViewClass: VideoView, collection: videos, el: $('#videos')[0]}
    );
    document.selectedVideoView = new SelectedVideoView({el: $('#selected_video')[0]});
});
