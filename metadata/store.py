import json
from time import time
from pyres import ResQ

from metadata import vimeo
from redis_connection import _key
import redis_connection as rc

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
        return data_dict

    def load(self):
        try:
            data = self._from_store()
        except NotFoundException:
            data = self._from_api()
        self.__dict__.update(data)
        return self

    def load_if_present(self):
        """Raises NotFoundException if not already stored.
        """
        data = self._from_store()
        self.__dict__.update(data)
        return self

    def queue_load(self):
        """Enqueue a task to load this metadata from the api,
        and store it."""
        pass

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
                return float(self.stats_number_of_likes) / self.stats_number_of_plays
        except AttributeError:
            raise NotFoundException

class MetaDataFetchTimes(object):
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
    if last_fetch is None or now - last_fetch > 3600:
        MetaDataFetchTimes.set(vimeo_id, now)
        resq.enqueue(FetchVimeoDataTask, vimeo_id)

class FetchVimeoDataTask(object):
    queue = 'vimeo'

    @staticmethod
    def perform(vimeo_id):
        try:
            VimeoMetadata(vimeo_id)._from_api()
        except vimeo.InvalidvimeoId:
            print 'invalid vimeo id'
            return
        except vimeo.ApiCallFailed:
            raise

