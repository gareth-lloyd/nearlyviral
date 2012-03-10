from redis import Redis
import settings

STORAGE_PREFIX = 'LKS'
LANG = 'LNG'
FOLLOWERS = 'FOL'
TIMEZONE = 'TZ'

r = Redis(db=settings.REDIS_DB)

def _key(*parts):
    return ':'.join(parts)

class UserProperty(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def get(self, user_id):
        return r.get(_key(self.prefix, str(user_id)))

    def set(self, user_id, property):
        if property is None:
            property = 'None'
        r.set(_key(self.prefix, str(user_id)), property)

class UserLinkSet(object):
    PREFIX = 'UL'
    def __init__(self, dt):
        self.key = _key(self.PREFIX, dt.strftime('%Y%m%d%H'))

    def update(self, user_id, identifier):
        """Returns 1 if the user has not linked before, and we
        therefore recorded the link, otherwise 0.
        """
        return r.sadd(self.key, _key(str(user_id), identifier))

    def all(self):
        return r.smembers(self.key)

class HourSet(object):
    def __init__(self, prefix, dt):
        self.key = _key(prefix, dt.strftime('%Y%m%d%H'))

    def update(self, url):
        if not url:
            return
        r.zincrby(self.key, url, 1.0)

    def popular(self):
        return r.zrevrange(self.key, 0, 20, withscores=True)
