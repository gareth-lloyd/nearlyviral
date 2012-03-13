import json
from datetime import date

from gather.score import top_scoring
from metadata.store import VimeoMetadata

from flask import Flask
app = Flask(__name__)

@app.route("/videos/")
def popular():
    ret = []
    for id, score in top_scoring():
        ret.append(VimeoMetadata(id).load().__dict__)

    return json.dumps(ret)

if __name__ == "__main__":
    app.run(debug=True)
