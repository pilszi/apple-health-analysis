from flask import Flask, Response, render_template, jsonify
import requests

app = Flask(__name__)

fastapi_path = "http://127.0.0.1:8000"


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/trigger-convert', methods=['get'])
def trigger_convert():
    try:

        
        # Flask에서 FastAPI로 요청 전달
        response = requests.get(f"{fastapi_path}/run-script")
        fastapi_result = response.json()
        
        # FastAPI의 결과를 브라우저로 다시 전달
        return jsonify({"status": "success", "message": fastapi_result.get("result")})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)