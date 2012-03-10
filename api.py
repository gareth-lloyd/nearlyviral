import json
from datetime import date

from watchlinks.analyze import most_popular

from flask import Flask
app = Flask(__name__)

videos = [
    {
        'id': 'e5uFBYKHpVk',
        'type': 'youtube',
        'title': 'Ron Paul Smacks Down Fox Moderators on Military/Defense Spending!',
        'description': None,
        'views': 442,
        'created': date(2012, 3, 5).isoformat(),
    },
    {
        'id': '5uFBYKHpVk',
        'type': 'youtube',
        'title': 'Ron Paul Smacks Down Fox Moderators on Military/Defense Spending!',
        'description': None,
        'views': 442,
        'created': date(2012, 3, 5).isoformat(),
    },
]

@app.route("/videos/")
def popular():
    #return json.dumps(list(most_popular()))
    return json.dumps(videos)

if __name__ == "__main__":
    app.run(debug=True)
