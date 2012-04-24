from time import time

from tests import RedisTestCase
from metadata.store import VimeoMetadata
from metadata import store
import redis_connection as rc

class VimeoMetaDataTests(RedisTestCase):
    def setUp(self):
        super(VimeoMetaDataTests, self).setUp()
        self.metadata = VimeoMetadata('123')
        store.vimeo.vimeo_data = lambda x: {'somekey': 'value'}

    def test_present(self):
        self.assertFalse(self.metadata.present())
        self.metadata._fetch_and_save_data()
        self.assertTrue(self.metadata.present())

    def test_needs_refresh(self):
        self.metadata._fetch_and_save_data()
        self.assertFalse(self.metadata.needs_refresh())

        rc.conn.expire(self.metadata.key, 3599)
        self.assertTrue(self.metadata.needs_refresh())

class MaybeFetchTests(RedisTestCase):
    def setUp(self):
        super(MaybeFetchTests, self).setUp()
        self.calls = []
        def assertion(*args, **kwargs):
            self.calls.append(True)

        store.resq.enqueue = assertion
        store.vimeo.vimeo_data = lambda x: {'somekey': 'value'}

    def test_wont_fetch_unless_recent_or_expiring(self):
        metadata = VimeoMetadata('123')
        metadata._fetch_and_save_data()
        store.maybe_fetch_metadata('123')
        self.assertFalse(self.calls)

        rc.conn.expire(metadata.key, 3599)
        store.maybe_fetch_metadata('123')
        self.assertTrue(self.calls.pop())

    def test_fetches_if_not_present(self):
        self.assertFalse(self.calls)

        store.maybe_fetch_metadata('abc')
        self.assertTrue(self.calls.pop())
