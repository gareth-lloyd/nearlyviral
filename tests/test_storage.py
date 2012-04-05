from tests import RedisTestCase
from gather.store import TwitterComments


class TwitterCommentsTests(RedisTestCase):
    def setUp(self):
        super(TwitterCommentsTests, self).setUp()
        self.comments = TwitterComments('abc')

    def test_empty(self):
        self.assertEquals([], self.comments.list())

    def test_add_comment(self):
        self.assertEquals(0, len(self.comments.list()))

        comment_dict = {'id': '123', 'text': 'cool'}
        self.comments.add_comment(comment_dict)

        self.assertEquals(1, len(self.comments.list()))

    def test_add_past_max(self):
        self.comments.add_comment({'id': '123', 'text': 'cool'})
        self.comments.add_comment({'id': '124', 'text': 'cool'})
        self.comments.add_comment({'id': '125', 'text': 'cool'})

        self.assertEquals(3, len(self.comments.list()))
        comment_dict = {'id': '126', 'text': 'cool'}
        self.comments.add_comment(comment_dict)

        self.assertEquals(3, len(self.comments.list()))
        self.assertEquals('126', self.comments.list()[0]['id'])
