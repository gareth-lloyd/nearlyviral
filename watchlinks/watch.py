from datetime import datetime
from twistedstream import protocol
from pyres import ResQ

from watchlinks.store import (HourSet, UserLinkSet, UserProperty,
        LANG, FOLLOWERS, TIMEZONE, STORAGE_PREFIX)
from metadata.store import FetchVimeoDataTask
from watchlinks.analyze import vimeo_id

resq = ResQ()

def user_linked_before(identifier, user_id):
    link_set = UserLinkSet(datetime.now())
    return not link_set.update(user_id, identifier)

class LinkReceiver(protocol.IStreamReceiver):
    def status(self, json_obj):
        try:
            user_id = json_obj['user']['id_str']
            for url_info in json_obj['entities']['urls']:
                identifier = vimeo_id(url_info['expanded_url'])
                if not identifier:
                    print 'No vid link %s' % url_info['expanded_url']
                    continue
                UserLinkSet(datetime.now()).update(user_id, identifier)

                followers = json_obj['user']['followers_count']
                UserProperty(FOLLOWERS).set(user_id, followers)

                tz = json_obj['user']['time_zone']
                UserProperty(TIMEZONE).set(user_id, tz)

                lang = json_obj['user']['lang']
                UserProperty(LANG).set(user_id, lang)

                resq.enqueue(FetchVimeoDataTask, identifier)
                print identifier

        except Exception,e :
            print e

    def disconnected(self, reason):
        print 'disconnected from twitter streaming API at %s' % datetime.now()

