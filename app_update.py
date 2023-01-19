from flask import Flask, jsonify, request
from yolo_detection_images import detectObjects
from re import DEBUG, sub
from flask import Flask, render_template, request, redirect, send_file, url_for, request, jsonify
from werkzeug.utils import secure_filename, send_from_directory
import os
import subprocess
import time


app = Flask(__name__)
app.debug = True
UPLOAD_FOLDER = 'images'
#UPLOAD_FOLDER = 'http://127.0.0.1:5000/myapp/detectObjects?image='
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

uploads_dir = os.path.join(app.instance_path, 'images')
uploaded = os.path.join(app.instance_path, 'uploads')
#uploaded = os.path.join(app.config['UPLOAD_FOLDER'])

os.makedirs(uploads_dir, exist_ok=True)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files[]')

    errors = {}
    success = False

    for file in files:      
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ts = time.time()
            filename = str(ts) + '-'+filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = True
            savefilename = filename
    img_path = 'images/' +savefilename
    results = detectObjects(img_path)
    return jsonify(results)
    
@app.route('/object_detection', methods=['POST'])
def processed_img():
    img_path = request.args.get('img_url')
    #allowed_file(img_path)
    results = detectObjects(img_path)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug = Flask, host='0.0.0.0' )