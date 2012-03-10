import math
from datetime import datetime
from collections import defaultdict

from store import (HourSet, UserLinkSet, UserProperty,
        LANG, FOLLOWERS, TIMEZONE, STORAGE_PREFIX)

def stripped_lines(f):
    return set(filter(None, map(lambda x: x.strip(), f.readlines())))

with open('en_timezones.txt', 'r') as tz_file:
    EN_TIMEZONES = stripped_lines(tz_file)

with open('all_timezones.txt', 'r') as tz_file:
    ALL_TIMEZONES = stripped_lines(tz_file)

def language_score(timezone, lang):
    if timezone in EN_TIMEZONES:
        return 15
    return 0

class UserLink(object):
    def __init__(self, user_link_key):
        self.user_id, self.identifier = user_link_key.split(':')
        user_followers = UserProperty(FOLLOWERS).get(self.user_id)
        if user_followers == 'None':
            self.user_followers = 0
        else:
            self.user_followers = int(user_followers)

        self.timezone = UserProperty(TIMEZONE).get(self.user_id)
        self.lang = UserProperty(LANG).get(self.user_id)

        if self.identifier.isdigit():
            self.type = 'vimeo'
        else:
            self.type = 'youtube'

    def score(self):
        return (
            math.log(self.user_followers) if self.user_followers else 0 +
            language_score(self.timezone, self.lang)
        )


def make_user_links(dt):
    user_link_set = UserLinkSet(dt)
    return map(UserLink, user_link_set.all())

def scores(user_links):
    id_scores = defaultdict(int)
    for user_link in user_links:
        id_scores[user_link.identifier] += user_link.score()

    return list(reversed(sorted(id_scores.iteritems(), key=lambda x: x[1])))

def scores_for_dt(dt):
    u = UserLinkSet(dt)
    user_links = map(UserLink, u.all())
    return scores(user_links)
