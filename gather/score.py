from collections import defaultdict
from datetime import datetime, timedelta

from gather.store import VideoProperty, UserLinkSet, HourSet, ENGLISH_LINKS
from metadata.store import VimeoMetadata
from redis_connection import r

PLAYS = 'PLS'
LIKES_OVER_PLAYS = 'LOP'
COMMENTS_OVER_PLAYS = 'LOC'
comments = VideoProperty(COMMENTS_OVER_PLAYS)
likes = VideoProperty(LIKES_OVER_PLAYS)
plays = VideoProperty(PLAYS)

EN_TIMEZONES = ['Adelaide', 'Alaska', 'Amsterdam', 'Arizona',
    'Atlantic Time (Canada)', 'Auckland', 'Brisbane', 'Hawaii', 'Canberra',
    'Indiana (East)', 'London', 'Melbourne', 'Mountain Time (US & Canada)',
    'Newfoundland', 'Pacific Time (US & Canada)', 'Perth', 'Pretoria',
    'Saskatchewan', 'Sydney', 'Wellington', 'Central Time (US & Canada)',
    'Darwin', 'Dublin', 'Eastern Time (US & Canada)', 'Edinburgh',
    'Georgetown']

def english_speaking(timezone, lang, text):
    """No offense intended to non-English speakers, but I found links that were
    of more interest to me by filtering on the presumed first language of the
    person that's linking. This is a very unreliable way of doing this. Might
    build something better at detecting language later. """
    return 1 if timezone in EN_TIMEZONES else 0

def set_vimeo_properties():
    from metadata.vimeo import InvalidVideoId
    for user_link in UserLinkSet().all():
        _, vimeo_id = user_link.split(':')
        try:
            metadata = VimeoMetadata(vimeo_id).load()
        except InvalidVideoId:
            print 'vimeo id %s is invalid' % vimeo_id
            continue
        print metadata
        comments.update(vimeo_id, metadata.comments_over_plays())
        likes.update(vimeo_id, metadata.likes_over_plays())
        plays.update(vimeo_id, metadata.stats_number_of_plays)

def top_scoring(hours=8):
    id_links = defaultdict(float)
    for hour in range(hours):
        h = HourSet(ENGLISH_LINKS, datetime.now() - timedelta(hours=hour))
        for vimeo_id, links in h.popular(100):
            id_links[vimeo_id] += links

    print list(reversed(sorted(id_links.iteritems(), key=lambda x: x[1])))[:20]

    final_scores = {}
    for vimeo_id, num_links in id_links.iteritems():
        if 100 < plays.member_score(vimeo_id) < 10000:
            multiplier = (likes.member_score(vimeo_id) +
                    100 * comments.member_score(vimeo_id))
            final_scores[vimeo_id] = multiplier * num_links
            print 'links before',num_links, 'links after', multiplier * num_links
    print len(final_scores)

    return list(reversed(sorted(final_scores.items(), key=lambda x: x[1])))[:20]

