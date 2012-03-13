from datetime import datetime
from redis_connection import _key
import redis_connection as rc

from metadata.store import SortedProperty

ENGLISH_LINKS = 'ENL'
NON_ENGLISH_LINKS = 'NEL'
TOTAL_AUDIENCE = 'AUD'

class UserLinkSet(object):
    KEY = 'UL'

    def update(self, user_id, vimeo_id):
        """Returns 1 if the user has not linked before, and we
        therefore recorded the link, otherwise 0.
        """
        return rc.conn.sadd(self.KEY, _key(str(user_id), vimeo_id))

    def all(self):
        return rc.conn.smembers(self.KEY)

class HourSet(SortedProperty):
    """Wraps a redis sorted set. We can get a separate set for each
    hour to divide up our data.
    """
    def __init__(self, prefix, dt=None):
        if dt is None:
            dt = datetime.now()
        self.key = _key(prefix, dt.strftime('%Y%m%d%H'))

