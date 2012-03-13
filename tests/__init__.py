from unittest import TestCase
import redis_connection
from redis import Redis
import settings

class RedisTestCase(TestCase):
    def setUp(self):
        super(RedisTestCase, self).setUp()
        test_redis = Redis(db=settings.TEST_REDIS_DB)
        test_redis.flushdb()
        redis_connection.conn = test_redis

