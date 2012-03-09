import json
from watchlinks.analyze import most_popular

from flask import Flask
app = Flask(__name__)

@app.route("/")
def popular():
    return json.dumps(list(most_popular()))

if __name__ == "__main__":
    app.run(debug=True)
