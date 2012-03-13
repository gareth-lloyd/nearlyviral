from collections import defaultdict
from datetime import datetime, timedelta

from gather.store import HourSet, ENGLISH_LINKS
from metadata.store import (SortedProperty, PLAYS, LIKES_OVER_PLAYS,
        COMMENTS_OVER_PLAYS)


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

def top_scoring(hours=8):
    likes = SortedProperty(LIKES_OVER_PLAYS)
    comments = SortedProperty(COMMENTS_OVER_PLAYS)
    plays = SortedProperty(PLAYS)

    id_links = defaultdict(float)
    for hour in range(hours):
        h = HourSet(ENGLISH_LINKS, datetime.now() - timedelta(hours=hour))
        for vimeo_id, links in h.top(100):
            id_links[vimeo_id] += links

    final_scores = {}
    for vimeo_id, num_links in id_links.iteritems():
        if 100 < plays.member_score(vimeo_id) < 10000:
            multiplier = (likes.member_score(vimeo_id) +
                    100 * comments.member_score(vimeo_id))
            final_scores[vimeo_id] = multiplier * num_links

    return list(reversed(sorted(final_scores.items(), key=lambda x: x[1])))[:20]

