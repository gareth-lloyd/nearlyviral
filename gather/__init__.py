from datetime import datetime
from twistedstream import protocol
from pyres import ResQ
from urlparse import urlparse

from gather.store import (HourSet, UserLinkSet,
        ENGLISH_LINKS, NON_ENGLISH_LINKS, TOTAL_AUDIENCE)
from gather.score import english_speaking


resq = ResQ()
link_set = UserLinkSet()

def vimeo_id(url):
    url = url or ''
    scheme, domain, path, params, query, fragment = urlparse(url)

    if domain.lower() in ('vimeo.com', 'www.vimeo.com', 'player.vimeo.com'):
        for path_segment in path.split('/'):
            if path_segment.isdigit():
                return path_segment
        if fragment.isdigit():
            return fragment
    return False

def user_linked_before(identifier, user_id):
    return not link_set.update(user_id, identifier)

def maybe_fetch_data(identifier):
    from metadata.store import (FetchVimeoDataTask, VimeoMetadata,
                NotFoundException)
    try:
        VimeoMetadata(identifier).load_if_present()
    except NotFoundException:
        resq.enqueue(FetchVimeoDataTask, identifier)

class LinkReceiver(protocol.IStreamReceiver):
    def status(self, json_obj):
        try:
            user_id = json_obj['user']['id_str']
            for url_info in json_obj['entities']['urls']:
                identifier = vimeo_id(url_info['expanded_url'])
                if not identifier or user_linked_before(identifier, user_id):
                    print 'No vid link %s' % url_info['expanded_url']
                    continue

                followers = json_obj['user']['followers_count']

                HourSet(TOTAL_AUDIENCE).update(identifier, followers)

                timezone = json_obj['user']['time_zone']
                lang = json_obj['user']['lang']
                text = json_obj['text']
                if english_speaking(timezone, lang, text):
                    HourSet(ENGLISH_LINKS).update(identifier)
                else:
                    HourSet(NON_ENGLISH_LINKS).update(identifier)
                maybe_fetch_data(identifier)

        except Exception,e :
            print e

    def disconnected(self, reason):
        print 'disconnected from twitter streaming API at %s' % datetime.now()

