from urlparse import urlparse
from collections import defaultdict
from datetime import datetime, timedelta

from store import HourSet

def most_popular(hours=6):
    from watch import STORAGE_PREFIX
    link_scores = defaultdict(int)
    for h in range(hours):
        hs = HourSet(STORAGE_PREFIX, datetime.now() - timedelta(hours=h))
        for link, score in hs.popular():
            link_scores[link] += (hours - h) * score

    return reversed(sorted(link_scores.iteritems(), key=lambda item: item[1]))

def get_query_arg(query, arg):
    for segment in query.split('&'):
        try:
            key, value = segment.split('=')
        except ValueError:
            continue
        if key == arg:
            return value
    raise KeyError

def vid_identifier(url):
    url = url or ''
    scheme, domain, path, params, query, fragment = urlparse(url)

    if domain in('youtube.com', 'www.youtube.com'):
        try:
            return get_query_arg(query, 'v')
        except KeyError:
            if path.startswith('/v/'):
                return path.strip('v/')

    elif domain == 'youtu.be':
        return path.lstrip('/')

    elif domain == 'm.youtube.com':
        try:
            return get_query_arg(fragment.split('?')[1], 'v')
        except KeyError:
            try:
                return get_query_arg(query, 'v')
            except KeyError:
                pass

    elif domain in ('vimeo.com', 'www.vimeo.com'):
        path = path.lstrip('/m')
        if path.isdigit():
            return path

    return False
