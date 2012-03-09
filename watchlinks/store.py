from redis import Redis

r = Redis()

class HourSet(object):
    def __init__(self, prefix, dt):
        self.key = '%s:%s' % (prefix, dt.strftime('%Y%m%d%H'))

    def update(self, url):
        if not url:
            return
        r.zincrby(self.key, url, 1.0)

    def popular(self):
        return r.zrevrange(self.key, 0, 20, withscores=True)
