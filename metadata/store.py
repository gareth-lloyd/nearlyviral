from metadata import vimeo
import json
from redis_connection import r, _key

class NotFoundException(Exception):
    pass

class VimeoMetadata(object):
    PREFIX = 'VMT'

    def __init__(self, video_id):
        self.key = _key(self.PREFIX, video_id)
        self.video_id = video_id)

    def _from_store(self):
        raw_data = r.get(self.key)
        if not raw_data:
            raise NotFoundException
        else:
            return json.loads(raw_data.decode('utf8'))

    def _from_api(self):
        raw_data = vimeo.video_data(self.video_id)
        #debug type - assume it's str
        print type(raw_data)
        r.set(self.key, raw_data)
        return json.loads(raw_data)

    def load(self):
        try:
            data = self._from_store()
        except NotFoundException:
            data = self._from_api()
        self.__dict__.update(data)

    def load_if_present(self):
        """Raises NotFoundException if not already stored.
        """
        data = self._from_store()

    def queue_load(self):
        """Enqueue a task to load this metadata from the api,
        and store it."""
        pass

def load_vimeo_metadata(video_id):
    VimeoMetadata(video_id)._from_api()
