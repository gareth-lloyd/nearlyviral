from datetime import datetime
from redis_connection import _key
import redis_connection as rc

ENGLISH_LINKS = 'ENL'
NON_ENGLISH_LINKS = 'NEL'
TOTAL_AUDIENCE = 'AUD'

class UserLinkSet(object):
    KEY = 'UL'

    def update(self, user_id, identifier):
        """Returns 1 if the user has not linked before, and we
        therefore recorded the link, otherwise 0.
        """
        return rc.conn.sadd(self.KEY, _key(str(user_id), identifier))

    def all(self):
        return rc.conn.smembers(self.KEY)

class HourSet(object):
    def __init__(self, prefix, dt=None):
        if dt is None:
            dt = datetime.now()
        self.key = _key(prefix, dt.strftime('%Y%m%d%H'))

    def update(self, identifier, score=1.0):
        if not identifier:
            return
        rc.conn.zincrby(self.key, identifier, score)

    def member_score(self, identifier):
        return rc.conn.zscore(self.key, identifier)

    def popular(self, limit=20):
        return rc.conn.zrevrange(self.key, 0, limit, withscores=True)

class VideoProperty(object):
    def __init__(self, key, dt=None):
        self.key = key

    def update(self, identifier, score=1.0):
        if not identifier:
            return
        rc.conn.zadd(self.key, identifier, score)

    def member_score(self, identifier):
        return rc.conn.zscore(self.key, identifier)

    def top(self, limit=20):
        return rc.conn.zrevrange(self.key, 0, limit, withscores=True)

    def bottom(self, limit=20):
        return rc.conn.zrange(self.key, 0, limit, withscores=True)
