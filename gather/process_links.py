import requests
from urlparse import urlparse

import redis_connection as rc


class ShortenedLink(object):

    def __init__(self, shortened_url):
        self.key = 'SHL:%s' % shortened_url

    def associate_with_vimeo_id(self, vimeo_id):
        rc.conn.set(self.key, vimeo_id)

    def resolve(self):
        return rc.conn.get(self.key)

class ShortenedLinkResolutionTask(object):
    queue = 'vimeo'

    @staticmethod
    def perform(shortened_url):
        response = requests.head(shortened_url)
        if response.status_code == 302:
            resolved_url = response.headers['location']

def vimeo_id_from_url(url):
    url = url or ''
    scheme, domain, path, params, query, fragment = urlparse(url)

    if domain.lower() in ('vimeo.com', 'www.vimeo.com', 'player.vimeo.com'):
        for path_segment in path.split('/'):
            if path_segment.isdigit():
                return path_segment
        if fragment.isdigit():
            return fragment
    else:
        shortened_link = ShortenedLink(url)
        vimeo_id = shortened_link.resolve()
        if vimeo_id:
            return vimeo_id

    return False
