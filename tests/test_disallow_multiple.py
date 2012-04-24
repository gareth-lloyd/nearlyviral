from tests import RedisTestCase
from gather.store import UserLinkRecord, DOUBLE_LINK_EXCLUSION_TIME
import redis_connection as rc

class DisallowMultipleLinksTests(RedisTestCase):
    def test_user_linked_before(self):
       self.assertFalse(UserLinkRecord.has_linked_before('abc', '123'))
       self.assertTrue(UserLinkRecord.has_linked_before('abc', '123'))

       # same user can link to other stuff
       self.assertFalse(UserLinkRecord.has_linked_before('abcd', '123'))

       # different users can link to same stuff
       self.assertFalse(UserLinkRecord.has_linked_before('abc', '1234'))
       ttl = rc.conn.ttl('UL:abc:1234') 

       # link should have been set up to expire
       self.assertTrue(isinstance(ttl, long))
       self.assertTrue(ttl <= DOUBLE_LINK_EXCLUSION_TIME)
