from collections import defaultdict
from datetime import datetime, timedelta
import math

from gather.store import HourSet, ENGLISH_LINKS, NON_ENGLISH_LINKS
from metadata.store import SortedProperty, PLAYS, LIKES_OVER_PLAYS

LIKES = SortedProperty(LIKES_OVER_PLAYS)
PLAYS = SortedProperty(PLAYS)
HOURS_BACK = 6

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

def score(vimeo_id, num_links):
    plays = PLAYS.member_score(vimeo_id) or 0
    if 1000 < plays < 1000000:
        multiplier = math.sqrt(LIKES.member_score(vimeo_id) or 0)
        return num_links * multiplier
    else:
        return 0

def link_counts(hours=HOURS_BACK):
    id_links = defaultdict(float)
    for hour in range(hours):
        en = HourSet(ENGLISH_LINKS, datetime.now() - timedelta(hours=hour))
        nen = HourSet(NON_ENGLISH_LINKS, datetime.now() - timedelta(hours=hour))
        for vimeo_id, links in en.top(50):
            # add the english links plus a proportion of any other links
            id_links[vimeo_id] += links + (0.3 * (nen.member_score(vimeo_id) or 0))
    return id_links.iteritems()

def top_scoring():
    final_scores = [(vimeo_id, score(vimeo_id, num_links))
            for vimeo_id, num_links in link_counts()]
    return list(reversed(sorted(final_scores, key=lambda x: x[1])))[:20]

def most_linked():
    return list(reversed(sorted(link_counts(), key=lambda x: x[1])))[:20]
