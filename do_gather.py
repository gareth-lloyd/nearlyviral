from watchlinks.watch import LinkReceiver
from twisted.internet import reactor

from oauth import oauth
from twistedstream import Stream, protocol

import settings

CONSUMER = oauth.OAuthConsumer(settings.TWITTER_CONSUMER_KEY,
                           settings.TWITTER_CONSUMER_SECRET)
TOKEN = oauth.OAuthToken(settings.TWITTER_APP_ACCESS_TOKEN,
                     settings.TWITTER_APP_ACCESS_TOKEN_SECRET)
STREAM = Stream(CONSUMER, TOKEN)

if __name__ == '__main__':
    keywords = ['vimeo']
    d = STREAM.track(LinkReceiver(), keywords)
    def started(arg):
        print 'started watching'
    d.addCallback(started)
    reactor.run()
