from tests import RedisTestCase
from metadata.store import VimeoMetadata
from api import popular, permitted_user
import api

class BannedUploadersTests(RedisTestCase):

    def test_permitted_user(self):
        banned_user = 'chris brown'
        api.BANNED_UPLOADERS = set([banned_user])

        self.banned_vid = VimeoMetadata('123')
        self.banned_vid._populate({'user_name': banned_user})
        self.assertFalse(permitted_user(self.banned_vid))

        self.normal_vid = VimeoMetadata('234')
        self.normal_vid._populate({'user_name': 'normal dude'})
        self.assertTrue(permitted_user(self.normal_vid))
