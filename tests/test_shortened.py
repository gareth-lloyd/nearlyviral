from tests import RedisTestCase
from gather import vimeo_id_from_url
from gather.process_links import (ShortenedLink, LINK_IS_NOT_VIMEO, resq,
          requests, LINK_TTL)

import redis_connection as rc

shortened_url = 'http://bit.ly/lsadkfj'
vimeo_id = '123'

class MockResponse(object):
    def __init__(self):
        self.headers = {'location': 'http://vimeo.com/1234'}
        self.status_code = 302

class ShortenedLinkTests(RedisTestCase):
    def setUp(self):
        super(ShortenedLinkTests, self).setUp()
        self.enqueue_calls = []
        def mock_enqueue(*args, **kwargs):
            self.enqueue_calls.append(True)
        resq.enqueue = mock_enqueue

    def test_resolve(self):
        sl = ShortenedLink(shortened_url)
        self.assertEquals(None, sl.resolve())
        sl.associate_with_vimeo_id(vimeo_id)
        self.assertEquals(vimeo_id, sl.resolve())

        ttl = rc.conn.ttl(sl.key)
        self.assertTrue(0 < ttl <= LINK_TTL)

    def test_urls_can_be_marked_unresolvable(self):
        sl = ShortenedLink(shortened_url)
        sl.not_vimeo()
        self.assertEquals(LINK_IS_NOT_VIMEO, sl.resolve())

        ttl = rc.conn.ttl(sl.key)
        self.assertTrue(0 < ttl <= LINK_TTL)

    def test_shortened_form_exists(self):
        sl = ShortenedLink(shortened_url)
        rc.conn.set(sl.key, vimeo_id)
        self.assertEquals(vimeo_id, vimeo_id_from_url(shortened_url))

    def test_shortened_form_does_not_exist(self):
        self.assertFalse(vimeo_id_from_url(shortened_url))

    def test_shortened_link_resolution_task_enqueued(self):
        vimeo_id_from_url(shortened_url)
        self.assertTrue(self.enqueue_calls)

    def test_non_vimeo_links_not_rechecked(self):
        sl = ShortenedLink(shortened_url)
        sl.not_vimeo()
        self.assertFalse(vimeo_id_from_url(shortened_url))
        self.assertFalse(self.enqueue_calls)

    def test_non_vimeo_links_get_marked_as_such(self):
        mock_response = MockResponse()
        mock_response.headers['location'] = 'http://google.com'
        requests.head = lambda *args, **kwargs: mock_response

        sl = ShortenedLink(shortened_url)
        sl.do_resolution()
        self.assertEquals(LINK_IS_NOT_VIMEO, sl.resolve())

    def test_vimeo_links_get_resolved(self):
        mock_response = MockResponse()
        requests.head = lambda *args, **kwargs: mock_response

        sl = ShortenedLink(shortened_url)
        sl.do_resolution()
        self.assertEquals('1234', sl.resolve())
