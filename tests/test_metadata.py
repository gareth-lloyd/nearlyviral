from time import time
from tests import RedisTestCase
from metadata import store


class MaybeFetchTests(RedisTestCase):
    def setUp(self):
        super(MaybeFetchTests, self).setUp()
        self.calls = []
        def assertion(*args, **kwargs):
            self.calls.append(True)

        store.resq.enqueue = assertion

    def test_wont_fetch_if_recent(self):
        self.assertFalse(self.calls)

        store.maybe_fetch_metadata('abc')
        self.assertTrue(self.calls.pop())

        store.maybe_fetch_metadata('abc')
        self.assertFalse(self.calls)

    def test_fetches_if_not_present(self):
        self.assertFalse(self.calls)

        store.maybe_fetch_metadata('abc')
        self.assertTrue(self.calls.pop())

    def test_fetches_if_old(self):
        self.assertFalse(self.calls)

        now = time()
        store.MetaDataFetchTimes.set('abc', now - 3700)

        store.maybe_fetch_metadata('abc')
        self.assertTrue(self.calls.pop())
