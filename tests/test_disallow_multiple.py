from tests import RedisTestCase
from gather import user_linked_before

class DisallowMultipleLinksTests(RedisTestCase):
    pass
    def test_user_linked_before(self):
       self.assertFalse(user_linked_before('abc', '123'))
       self.assertTrue(user_linked_before('abc', '123'))

       # same user can link to other stuff
       self.assertFalse(user_linked_before('abcd', '123'))

       # different users can link to same stuff
       self.assertFalse(user_linked_before('abc', '1234'))

