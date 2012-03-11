from urlparse import urlparse
from collections import defaultdict
from datetime import datetime, timedelta

from watchlinks.store import UserLinkSet
from watchlinks.score import UserLink

def most_popular(hours=3):
    link_scores = defaultdict(int)
    for h in range(hours):
        hs = UserLinkSet(datetime.now() - timedelta(hours=h))
        user_links = map(UserLink, hs.all())
        for user_link in user_links:
            link_scores[user_link.identifier] += user_link.score()

    return reversed(sorted(link_scores.iteritems(), key=lambda item: item[1]))

def vimeo_id(url):
    """
    """
    url = url or ''
    scheme, domain, path, params, query, fragment = urlparse(url)
    domain = domain.lower()

    if domain in ('vimeo.com', 'www.vimeo.com', 'player.vimeo.com'):
        for path_segment in path.split('/'):
            if path_segment.isdigit():
                return path_segment

        if fragment.isdigit():
            return fragment

    return False

