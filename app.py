#!flask/bin/python
from flask import Flask, abort, send_file, render_template, request, url_for

app = Flask(__name__)

@app.route('/api/')
def index():
    return render_template('upload.html', title='Upload DICOM')

@app.route('/api/upload/', methods=['POST'])
def upload():
    #pass (upload and convert dicom)
    return render_template('submit.html', title='DICOM Viewer')

@app.route('/api/upload/<int:img_id>', methods=['GET'])
def get_image(img_id):
    try:
       filename = 'images/IM-0001-'+ str(img_id).zfill(4) + '.jpg'
       return send_file(filename)
    except:
       filename = 'images/error.gif'
       return send_file(filename)

if __name__ == '__main__':
    host="localhost",
    port=int("8080")
    app.run(debug=True)
