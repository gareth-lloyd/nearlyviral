import json
from datetime import datetime, timedelta

from metadata import vimeo
from watchlinks.store import UserLinkSet

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
            try:
                data = self._from_api()
            except vimeo.InvalidVideoId:
                return
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

class VideosProperty(object):
    def __init__(self, key):
        self.key = key

    def update(self, member, score):
        r.zadd(self.key, member, float(score))

    def get_score(self, member):
        return r.zscore(self.key, member)


def ids(hours=4):
    all_ids = set()
    for x in range(hours):
        dt = datetime.now() - timedelta(hours=hours)
        u = UserLinkSet(dt)
        all_ids.update([ul.split(':')[1] for ul in u.all()])
    return all_ids

def store_metadata_for_id(video_id):
    data = VimeoMetadata(video_id).load()
    VideosProperty('likes').update(video_id, data.stats_number_of_likes)
    VideosProperty('plays').update(video_id, data.stats_number_of_plays)
    VideosProperty('comments').update(video_id, data.stats_number_of_comments)
