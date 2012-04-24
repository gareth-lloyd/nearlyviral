from datetime import datetime, timedelta
from redis_connection import _key
import redis_connection as rc
import simplejson as json

from metadata.store import SortedProperty

ENGLISH_LINKS = 'ENL'
NON_ENGLISH_LINKS = 'NEL'
DOUBLE_LINK_EXCLUSION_TIME = 24 * 60 * 60

class Count(object):
    def __init__(self, key):
        self.key = key

    def increment(self):
        rc.conn.incr(self.key)

    def get(self):
        return int(rc.conn.get(self.key))

class UserLinkRecord(object):
    @staticmethod
    def has_linked_before(user_id, vimeo_id):
        """Returns 1 if the user has not linked before, and we
        therefore recorded the link, otherwise 0.
        """
        key = 'UL:%s:%s' % (user_id, vimeo_id)
        if rc.conn.exists(key):
            return True
        else:
            # no need to worry about race conditions in current design
            rc.conn.set(key, 1)
            rc.conn.expire(key, DOUBLE_LINK_EXCLUSION_TIME)
            return False

class HourSet(SortedProperty):
    """Wraps a redis sorted set. We can get a separate set for each
    hour to divide up our data.
    """
    def __init__(self, prefix, dt=None):
        if dt is None:
            dt = datetime.now()
        self.key = _key(prefix, dt.strftime('%Y%m%d%H'))


class TwitterComments(object):
    """Manage stored twitter comments for a particular video. We
    only want to store a few recent comments.
    """
    MAX = 3
    EXPIRE_AFTER = 86400
    def __init__(self, video_id):
        self.key = _key('TLS', video_id)

    def add_comment(self, comment_dict):
        comment = json.dumps(comment_dict)
        with rc.conn.pipeline() as pipe:
            pipe.lpush(self.key, comment)
            pipe.ltrim(self.key, 0, self.MAX - 1)
            pipe.expire(self.key, self.EXPIRE_AFTER)
            pipe.execute()

    def list(self):
        return map(json.loads, rc.conn.lrange(self.key, 0, self.MAX - 1))

def remove_old(hours_back):
    now = datetime.now()
    for hours in range(24, 24+hours_back):
        dt = now - timedelta(hours=hours)
        for prefix in (ENGLISH_LINKS, NON_ENGLISH_LINKS):
            h = HourSet(prefix, dt)
            h.delete()

