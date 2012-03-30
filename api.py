import json

from gather.score import top_scoring
from metadata.store import VimeoMetadata
import redis_connection as rc

from flask import Flask
app = Flask(__name__)

CACHE_KEY = 'popular_cache'
CACHE_TTL = 600

@app.route("/videos/")
def popular():
    return_value = rc.conn.get(CACHE_KEY)
    if not return_value:
        videos_data = []
        for id, score in top_scoring():
            videos_data.append(VimeoMetadata(id).load().__dict__)
        return_value = json.dumps(videos_data)
        rc.conn.set(CACHE_KEY, return_value)
        rc.conn.expire(CACHE_KEY, CACHE_TTL)
    return return_value

if __name__ == "__main__":
    app.run(debug=True)
