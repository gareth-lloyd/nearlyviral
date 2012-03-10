from datetime import datetime
from twistedstream import Stream, protocol
from oauth import oauth
from twisted.internet import reactor

from store import (HourSet, UserLinkSet, UserProperty,
        LANG, FOLLOWERS, TIMEZONE, STORAGE_PREFIX)
from analyze import vid_identifier
import settings

CONSUMER = oauth.OAuthConsumer(settings.TWITTER_CONSUMER_KEY,
                           settings.TWITTER_CONSUMER_SECRET)
TOKEN = oauth.OAuthToken(settings.TWITTER_APP_ACCESS_TOKEN,
                     settings.TWITTER_APP_ACCESS_TOKEN_SECRET)
STREAM = Stream(CONSUMER, TOKEN)

def user_linked_before(identifier, user_id):
    link_set = UserLinkSet(datetime.now())
    return not link_set.update(user_id, identifier)

class InitialDataReceiver(protocol.IStreamReceiver):
    """record possibly relevant information about a link for
    analysis later
    """
    def status(self, json_obj):
        try:
            user_id = json_obj['user']['id_str']
            found_links = False
            for url_info in json_obj['entities']['urls']:
                identifier = vid_identifier(url_info['expanded_url'])
                if not identifier:
                    print 'No vid link %s' % url_info['expanded_url']
                    continue

                found_links = True
                UserLinkSet(datetime.now()).update(user_id, identifier)

            if found_links:
                followers = json_obj['user']['followers_count']
                UserProperty(FOLLOWERS).set(user_id, followers)

                tz = json_obj['user']['time_zone']
                UserProperty(TIMEZONE).set(user_id, tz)

                lang = json_obj['user']['lang']
                UserProperty(LANG).set(user_id, lang)

        except Exception,e :
            print e

class LinkReceiver(protocol.IStreamReceiver):
    def status(self, json_obj):
        try:
            user_id = json_obj['user']['id_str']
            followers = json_obj['user']['followers_count']
            is_english = json_obj['user']['lang'] == 'en'
            for url_info in json_obj['entities']['urls']:
                identifier = vid_identifier(url_info['expanded_url'])
                if not identifier:
                    print 'No vid link %s' % url_info['expanded_url']

                if identifier and not user_linked_before(identifier, user_id):
                    HourSet(STORAGE_PREFIX, datetime.now()).update(identifier)
        except Exception,e :
            print e

    def disconnected(self, reason):
        print 'disconnected from twitter streaming API at %s' % datetime.now()

if __name__ == '__main__':
    with open('keywords.txt', 'r') as f:
        keywords = set(filter(None, map(lambda x: x.strip(), f.readlines())))
    d = STREAM.track(InitialDataReceiver(), keywords)
    def started(arg):
        print 'started watching'
    d.addCallback(started)
    reactor.run()
