from datetime import datetime
from twistedstream import protocol, Stream
from twistedstream.stream import CONNECTED, CONNECTING
from urlparse import urlparse
from metadata.store import maybe_fetch_metadata
from oauth import oauth
from twisted.internet import reactor

from gather.store import (HourSet, UserLinkSet, Count,
        ENGLISH_LINKS, NON_ENGLISH_LINKS)
from gather.score import english_speaking
import settings

CONSUMER = oauth.OAuthConsumer(settings.TWITTER_CONSUMER_KEY,
                           settings.TWITTER_CONSUMER_SECRET)
TOKEN = oauth.OAuthToken(settings.TWITTER_APP_ACCESS_TOKEN,
                     settings.TWITTER_APP_ACCESS_TOKEN_SECRET)

STREAM = Stream(CONSUMER, TOKEN)
LINK_COUNT = Count('total_links')

link_set = UserLinkSet()

def vimeo_id_from_url(url):
    url = url or ''
    scheme, domain, path, params, query, fragment = urlparse(url)

    if domain.lower() in ('vimeo.com', 'www.vimeo.com', 'player.vimeo.com'):
        for path_segment in path.split('/'):
            if path_segment.isdigit():
                return path_segment
        if fragment.isdigit():
            return fragment
    return False

def user_linked_before(vimeo_id, user_id):
    return not link_set.update(user_id, vimeo_id)

class LinkReceiver(protocol.IStreamReceiver):
    def status(self, json_obj):
        try:
            user_id = json_obj['user']['id_str']
            for url_info in json_obj['entities']['urls']:
                url = url_info['expanded_url']
                vimeo_id = vimeo_id_from_url(url)
                if not vimeo_id:
                    print 'No vid link %s' % url
                    continue
                LINK_COUNT.increment()
                if user_linked_before(vimeo_id, user_id):
                    print 'multiple links by %s to %s' % (user_id, url)
                    continue

                timezone = json_obj['user']['time_zone']
                lang = json_obj['user']['lang']
                text = json_obj['text']
                if english_speaking(timezone, lang, text):
                    maybe_fetch_metadata(vimeo_id)
                    HourSet(ENGLISH_LINKS).increment(vimeo_id)
                else:
                    HourSet(NON_ENGLISH_LINKS).increment(vimeo_id)

        except Exception,e :
            print e

    def disconnected(self, reason):
        print 'disconnected from twitter streaming API at %s' % datetime.now()
        reactor.callLater(100, setup_receiver)

def setup_receiver():
    if STREAM.state in (CONNECTED, CONNECTING):
        return

    keywords = ['vimeo']
    def started(arg):
        print 'started watching'

    d = STREAM.track(LinkReceiver(), keywords)
    d.addCallback(started)

