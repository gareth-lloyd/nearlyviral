import json
import settings
from datetime import datetime, timedelta

from metadata import vimeo
from gather.store import UserLinkSet

from redis_connection import r, _key

class NotFoundException(Exception):
    pass

class VimeoMetadata(object):
    PREFIX = 'VMT'

    def __init__(self, video_id):
        self.key = _key(self.PREFIX, video_id)
        self.video_id = video_id

    def _from_store(self):
        raw_data = r.get(self.key)
        if not raw_data:
            raise NotFoundException
        else:
            return json.loads(raw_data.decode('utf8'))

    def _from_api(self):
        data_dict = vimeo.video_data(self.video_id)
        r.set(self.key, json.dumps(data_dict))
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

class FetchVimeoDataTask(object):
    queue = 'vimeo'

    @staticmethod
    def perform(video_id):
        try:
            VimeoMetadata(video_id).load()
        except InvalidVideoId, e:
            print 'invalid video id'
            return
        except ApiCallFailed:
            raise

