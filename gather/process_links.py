import requests
from urlparse import urlparse
from pyres import ResQ

import redis_connection as rc

resq = ResQ()
LINK_IS_NOT_VIMEO = 'notvimeo'
LINK_TTL = 24 * 60 * 60

class NonVimeoUrl(Exception):
    pass


class NonShortenedUrl(Exception):
    pass


def vimeo_id_from_url(url):
    try:
        return parse_vimeo_url(url)
    except NonVimeoUrl:
        shortened_link = ShortenedLink(url)
        resolved_id = shortened_link.resolve()
        if resolved_id and resolved_id != LINK_IS_NOT_VIMEO:
            return resolved_id
        elif resolved_id is None:
            resq.enqueue(ShortenedLinkResolutionTask, url)
    return False

def parse_vimeo_url(url):
    scheme, domain, path, params, query, fragment = urlparse(url or '')

    # if no domain, assume we've been handed a vimeo path
    if domain.lower() in ('', 'vimeo.com', 'www.vimeo.com', 'player.vimeo.com'):
        for path_segment in path.split('/'):
            if path_segment.isdigit():
                return path_segment
        if fragment.isdigit():
            return fragment
    raise NonVimeoUrl


class ShortenedLink(object):
    def __init__(self, shortened_url):
        self.shortened_url = shortened_url
        self.key = 'SHL:%s' % shortened_url

    def associate_with_vimeo_id(self, vimeo_id):
        rc.conn.set(self.key, vimeo_id)
        rc.conn.expire(self.key, LINK_TTL)

    def not_vimeo(self):
        self.associate_with_vimeo_id(LINK_IS_NOT_VIMEO)

    def resolve(self):
        return rc.conn.get(self.key)

    def do_resolution(self):
        response = requests.head(self.shortened_url)
        if response.status_code in (302, 301):
            url = response.headers['location']
        else:
            raise NonShortenedUrl

        try:
            vimeo_id = parse_vimeo_url(url)
            self.associate_with_vimeo_id(vimeo_id)
        except NonVimeoUrl:
            self.not_vimeo()


class ShortenedLinkResolutionTask(object):
    queue = 'vimeo'

    @staticmethod
    def perform(url):
        ShortenedLink(url).do_resolution()

