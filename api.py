import json
from datetime import date

from watchlinks.analyze import most_popular

from flask import Flask
app = Flask(__name__)

@app.route("/videos/")
def popular():
    ret = []
    top = list(most_popular())
    for link, score in top[:20]:
        ret.append({'id': link})

    return json.dumps(ret)

if __name__ == "__main__":
    app.run(debug=True)
