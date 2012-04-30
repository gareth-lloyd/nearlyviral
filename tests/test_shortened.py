from tests import RedisTestCase
from gather import vimeo_id_from_url
from gather.process_links import ShortenedLink

import redis_connection as rc

class ShortenedLinkTests(RedisTestCase):
    def test_resolve(self):
        shortened_url = 'http://bit.ly/lsadkfj'
        vimeo_id = '123'
        sl = ShortenedLink(shortened_url)
        self.assertEquals(None, sl.resolve())
        sl.associate_with_vimeo_id(vimeo_id)
        self.assertEquals(vimeo_id, sl.resolve())


    def test_shortened_form_exists(self):
        shortened_url = 'http://bit.ly/lsadkfj'
        vimeo_id = '123'
        sl = ShortenedLink(shortened_url)
        rc.conn.set(sl.key, vimeo_id)

        self.assertEquals(vimeo_id, vimeo_id_from_url(shortened_url))

    def test_shortened_form_does_not_exist(self):
        shortened_url = 'http://bit.ly/lsadkfj'
        self.assertFalse(vimeo_id_from_url(shortened_url))

