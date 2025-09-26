import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from analyze import read_image

# Load environment variables from .env
load_dotenv()

AZURE_CV_ENDPOINT = os.getenv("AZURE_CV_ENDPOINT")
AZURE_CV_KEY = os.getenv("AZURE_CV_KEY")

if not AZURE_CV_ENDPOINT or not AZURE_CV_KEY:
    raise RuntimeError("Missing AZURE_CV_ENDPOINT or AZURE_CV_KEY")

app = Flask(__name__, template_folder='templates')

@app.route("/")
def home():
    return render_template('index.html')

# API at /api/v1/analysis/
@app.route("/api/v1/analysis/", methods=['POST'])
def analysis():
    try:
        get_json = request.get_json()
        image_url = get_json['url']
    except Exception:
        return jsonify({'error': 'Missing URL in JSON'}), 400
    
    try:
        res = read_image(image_url)
        response_data = {"text": res}
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({'error': f'Error in processing: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)