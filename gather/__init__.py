from datetime import datetime
from twistedstream import protocol
from urlparse import urlparse
from metadata.store import maybe_fetch_metadata

from gather.store import (HourSet, UserLinkSet,
        ENGLISH_LINKS, NON_ENGLISH_LINKS, TOTAL_AUDIENCE)
from gather.score import english_speaking


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
                if user_linked_before(vimeo_id, user_id):
                    print 'multiple links by %s to %s' % (user_id, url)
                    continue

                followers = json_obj['user']['followers_count']

                HourSet(TOTAL_AUDIENCE).increment(vimeo_id, followers)

                timezone = json_obj['user']['time_zone']
                lang = json_obj['user']['lang']
                text = json_obj['text']
                if english_speaking(timezone, lang, text):
                    HourSet(ENGLISH_LINKS).increment(vimeo_id)
                else:
                    HourSet(NON_ENGLISH_LINKS).increment(vimeo_id)
                maybe_fetch_metadata(vimeo_id)

        except Exception,e :
            print e

    def disconnected(self, reason):
        print 'disconnected from twitter streaming API at %s' % datetime.now()

