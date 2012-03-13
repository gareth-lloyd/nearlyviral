from datetime import datetime
import settings
from redis_connection import r, _key

ENGLISH_LINKS = 'ENL'
NON_ENGLISH_LINKS = 'NEL'
TOTAL_AUDIENCE = 'AUD'

class UserLinkSet(object):
    KEY = 'UL'

    def update(self, user_id, identifier):
        """Returns 1 if the user has not linked before, and we
        therefore recorded the link, otherwise 0.
        """
        return r.sadd(self.KEY, _key(str(user_id), identifier))

    def all(self):
        return r.smembers(self.KEY)

class HourSet(object):
    def __init__(self, prefix, dt=None):
        if dt is None:
            dt = datetime.now()
        self.key = _key(prefix, dt.strftime('%Y%m%d%H'))

    def update(self, identifier, score=1.0):
        if not identifier:
            return
        r.zincrby(self.key, identifier, score)

    def member_score(self, identifier):
        return r.zscore(self.key, identifier)

    def popular(self, limit=20):
        return r.zrevrange(self.key, 0, limit, withscores=True)

class VideoProperty(object):
    def __init__(self, key, dt=None):
        self.key = key

    def update(self, identifier, score=1.0):
        if not identifier:
            return
        r.zadd(self.key, identifier, score)

    def member_score(self, identifier):
        return r.zscore(self.key, identifier)

    def top(self, limit=20):
        return r.zrevrange(self.key, 0, limit, withscores=True)

    def bottom(self, limit=20):
        return r.zrange(self.key, 0, limit, withscores=True)
