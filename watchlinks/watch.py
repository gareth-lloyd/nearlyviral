from datetime import datetime
from twistedstream import Stream
from twistedstream.protocol import IStreamReceiver
from oauth import oauth
from twisted.internet import reactor

from store import HourSet
from analyze import vid_identifier

import settings
CONSUMER = oauth.OAuthConsumer(settings.TWITTER_CONSUMER_KEY,
                           settings.TWITTER_CONSUMER_SECRET)
TOKEN = oauth.OAuthToken(settings.TWITTER_APP_ACCESS_TOKEN,
                     settings.TWITTER_APP_ACCESS_TOKEN_SECRET)
STORAGE_PREFIX = 'links'
STREAM = Stream(CONSUMER, TOKEN)

def do_watch(keywords):
    d = STREAM.track(LinkReceiver(), keywords)
    def started(arg):
        print 'started watching'
    d.addCallback(started)

def record_url(url):
    identifier = vid_identifier(url)
    print identifier

    if identifier:
        HourSet(STORAGE_PREFIX, datetime.now()).update(url)

def find_links(status):
    for url_info in status['entities']['urls']:
        record_url(url_info['expanded_url'])

class LinkReceiver(IStreamReceiver):
    def __init__(self):
        self.reconnects = 0

    def status(self, json_obj):
        find_links(json_obj)

    def disconnected(self, reason):
        print 'disconnected from twitter streaming API at %s' % datetime.now()
        print 'REASON:', reason
        if self.reconnects < 40:
            reactor.callLater(self.reconnects * 10, do_watch)

if __name__ == '__main__':
    with open('keywords.txt', 'r') as f:
        keywords = set(filter(None, f.readlines()))
    do_watch(keywords)
    reactor.run()
