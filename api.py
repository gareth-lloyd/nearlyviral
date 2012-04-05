import json

from gather.score import top_scoring
from gather import LINK_COUNT
from gather.store import TwitterComments
from metadata.store import VimeoMetadata
import redis_connection as rc

import settings
DEFAULTS = {
    'js_lib_dir': settings.JS_LIB_DIR,
    'js_dir': settings.JS_DIR,
    'css_dir': settings.CSS_DIR,
}

from flask import Flask
from flask import render_template
app = Flask(__name__)

CACHE_KEY = 'popular_cache'
CACHE_TTL = 600

@app.route("/")
def index():
    template_data = DEFAULTS
    template_data['num_links'] = LINK_COUNT.get()
    return render_template('index.html', **template_data)

@app.route("/videos/")
def popular():
    return_value = rc.conn.get(CACHE_KEY)
    if not return_value:
        videos = VimeoMetadata.load_multiple([id for id, _ in top_scoring()])
        videos_data = [video.__dict__ for video in videos]
        return_value = json.dumps(videos_data)
        rc.conn.set(CACHE_KEY, return_value)
        rc.conn.expire(CACHE_KEY, CACHE_TTL)
    return return_value

@app.route("/videos/<vimeo_id>/tweets/")
def tweets(vimeo_id):
    return json.dumps(TwitterComments(vimeo_id).list())

if __name__ == "__main__":
    app.run(debug=True)
