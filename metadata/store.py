import json
from time import time
from pyres import ResQ

from metadata import vimeo
from redis_connection import _key
import redis_connection as rc

PLAYS = 'PLS'
LIKES_OVER_PLAYS = 'LOP'
COMMENTS_OVER_PLAYS = 'LOC'

resq = ResQ()

class NotFoundException(Exception):
    pass

class VimeoMetadata(object):
    PREFIX = 'VMT'

    def __init__(self, vimeo_id):
        self.key = _key(self.PREFIX, vimeo_id)
        self.vimeo_id = vimeo_id

    def _from_store(self):
        raw_data = rc.conn.get(self.key)
        if not raw_data:
            raise NotFoundException
        else:
            return json.loads(raw_data.decode('utf8'))

    def _from_api(self):
        data_dict = vimeo.vimeo_data(self.vimeo_id)
        rc.conn.set(self.key, json.dumps(data_dict))
        self._populate(data_dict)

    def _populate(self, data):
        self.__dict__.update(data)

    def load(self):
        try:
            data = self._from_store()
        except NotFoundException:
            data = self._from_api()
        self._populate(data)
        return self

    def load_if_present(self):
        """Raises NotFoundException if not already stored.
        """
        data = self._from_store()
        self._populate(data)
        return self

    def likes_over_plays(self):
        try:
            if not self.stats_number_of_plays:
                return 0
            else:
                return float(self.stats_number_of_likes) / self.stats_number_of_plays
        except AttributeError:
            raise NotFoundException

    def comments_over_plays(self):
        try:
            if not self.stats_number_of_plays:
                return 0
            else:
                return float(self.stats_number_of_comments) / self.stats_number_of_plays
        except AttributeError:
            raise NotFoundException

    @staticmethod
    def load_multiple(ids):
        keys = [_key(VimeoMetadata.PREFIX, id) for id in ids]
        datas = rc.conn.mget(keys)
        objs = []
        for id, data in zip(ids, datas):
            if data:
                vimeo_metadata = VimeoMetadata(id)
                vimeo_metadata._populate(json.loads(data.encode('utf-8')))
                objs.append(vimeo_metadata)
        return objs

class SortedProperty(object):
    """Thin wrapper round a redis sorted set to store a numeric
    property of a video.
    """
    def __init__(self, key):
        self.key = key

    def increment(self, member, score=1.0):
        rc.conn.zincrby(self.key, member, score)

    def add_or_update(self, member, score=1.0):
        rc.conn.zadd(self.key, member, score)

    def member_score(self, member):
        return rc.conn.zscore(self.key, member)

    def top(self, limit=20):
        return rc.conn.zrevrange(self.key, 0, limit, withscores=True)

    def bottom(self, limit=20):
        return rc.conn.zrange(self.key, 0, limit, withscores=True)

    def delete(self):
        return rc.conn.delete(self.key)


class MetaDataFetchTimes(object):
    """Very thin wrapper round a redis sorted set to store the last
    time we fetched data for a particular vimeo video.
    """
    KEY = 'LMF'
    @staticmethod
    def get(vimeo_id):
        return rc.conn.zscore(MetaDataFetchTimes.KEY, vimeo_id)

    @staticmethod
    def set(vimeo_id, t):
        return rc.conn.zadd(MetaDataFetchTimes.KEY, vimeo_id, t)


def maybe_fetch_metadata(vimeo_id):
    now = time()
    last_fetch = MetaDataFetchTimes.get(vimeo_id)
    if last_fetch is None or (now - last_fetch) > 3600:
        MetaDataFetchTimes.set(vimeo_id, now)
        resq.enqueue(FetchVimeoDataTask, vimeo_id)


class FetchVimeoDataTask(object):
    queue = 'vimeo'

    @staticmethod
    def perform(vimeo_id):
        try:
            metadata = VimeoMetadata(vimeo_id)
            metadata._from_api()
            SortedProperty(COMMENTS_OVER_PLAYS).add_or_update(vimeo_id, metadata.comments_over_plays())
            SortedProperty(LIKES_OVER_PLAYS).add_or_update(vimeo_id, metadata.likes_over_plays())
            SortedProperty(PLAYS).add_or_update(vimeo_id, metadata.stats_number_of_plays)
        except vimeo.InvalidVideoId:
            print 'invalid vimeo id'
            return
        except vimeo.ApiCallFailed:
            raise

