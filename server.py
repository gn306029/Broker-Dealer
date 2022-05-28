from flask import Flask, json, request
from flask_cors import CORS
from stock import run
from datetime import datetime

app = Flask(__name__)
CORS(app)

target_broker = [
    ("9200", "9216"), # 凱基信義
    ("9A00", "0039004100390052"), # 永豐金信義
    ("8560", "8564"), # 新光台南
    ("7790", "003700370039005a"), # 國票安和
]

@app.route("/get")
def get_data():
    start_date = datetime.strptime(request.args.get('start_date'), "%Y-%m-%d").strftime("%Y-%#m-%d")
    end_date = datetime.strptime(request.args.get('end_date'), "%Y-%m-%d").strftime("%Y-%#m-%d")

    data = run({
        "target_broker": target_broker,
        "start_date": start_date,
        "end_date": end_date
    })

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )

    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

if __name__ == '__main__':
    app.run(port=8000, debug=True)