from redis import Redis
import settings

conn = Redis(db=settings.REDIS_DB)

def _key(*parts):
    return ':'.join(map(str, parts))

