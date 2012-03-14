from tests import RedisTestCase
from datetime import datetime, timedelta
from gather.store import ENGLISH_LINKS, NON_ENGLISH_LINKS, HourSet
from gather.score import (english_speaking, score, link_counts, top_scoring,
        LIKES, PLAYS)

VIMEO_ID = '123'
class ScoringTests(RedisTestCase):

    def test_english_speaking(self):
        self.assertTrue(english_speaking('London', None, None))
        self.assertFalse(english_speaking('Paris', None, None))

    def test_score_zero_for_too_many_plays(self):
        PLAYS.add_or_update(VIMEO_ID, 10000000)
        self.assertEquals(0, score(VIMEO_ID, 100))

    def test_score_zero_for_too_few_plays(self):
        PLAYS.add_or_update(VIMEO_ID, 99)
        self.assertEquals(0, score(VIMEO_ID, 100))

    def test_score(self):
        PLAYS.add_or_update(VIMEO_ID, 1001)
        LIKES.add_or_update(VIMEO_ID, 0.25)
        self.assertEquals(5, score(VIMEO_ID, 10))

    def test_link_counts_adds_previous_hours(self):
        now = datetime.now()
        HourSet(ENGLISH_LINKS, now).increment(VIMEO_ID)
        HourSet(ENGLISH_LINKS, now - timedelta(hours=1)).increment(VIMEO_ID)
        HourSet(ENGLISH_LINKS, now - timedelta(hours=2)).increment(VIMEO_ID)
        self.assertEquals(3, dict(link_counts())[VIMEO_ID])

    def test_link_counts_discounts_non_english(self):
        now = datetime.now()
        HourSet(ENGLISH_LINKS, now).increment(VIMEO_ID)
        HourSet(ENGLISH_LINKS, now - timedelta(hours=1)).increment(VIMEO_ID)
        HourSet(NON_ENGLISH_LINKS, now).increment(VIMEO_ID)
        HourSet(NON_ENGLISH_LINKS, now - timedelta(hours=1)).increment(VIMEO_ID)
        self.assertAlmostEquals(2.6, dict(link_counts())[VIMEO_ID])

    def test_top_scoring(self):
        vimeo_id_2 = '1234'
        now = datetime.now()
        HourSet(ENGLISH_LINKS, now).increment(VIMEO_ID)
        HourSet(ENGLISH_LINKS, now).increment(VIMEO_ID)
        HourSet(ENGLISH_LINKS, now).increment(vimeo_id_2)

        scores = top_scoring()
        self.assertEquals(VIMEO_ID, scores[0][0])
        self.assertEquals(vimeo_id_2, scores[1][0])

