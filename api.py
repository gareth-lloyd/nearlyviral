import json
from datetime import date

from watchlinks.analyze import most_popular
from metadata.store import VimeoMetadata

from flask import Flask
app = Flask(__name__)

@app.route("/videos/")
def popular():
    ret = []
    for id, score in list(most_popular())[:20]:
        ret.append(VimeoMetadata(id).load().__dict__)

    return json.dumps(ret)

if __name__ == "__main__":
    app.run(debug=True)
