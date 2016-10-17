#!flask/bin/python
from flask import Flask, abort, send_file, render_template, request, url_for
from flaskext.mysql import MySQL
import hashlib, uuid
import subprocess
import fnmatch
import settings
from os import listdir, makedirs, path

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = settings.database['user']
app.config['MYSQL_DATABASE_PASSWORD'] = settings.database['password']
app.config['MYSQL_DATABASE_DB'] = settings.database['db_name']
app.config['MYSQL_DATABASE_HOST'] = settings.database['host']
mysql.init_app(app)

@app.route('/api/')
def index():
    return render_template('upload.html', title='Upload DICOM')

# handles uploading Dicom files, converting into jpg format and storing into database
@app.route('/api/upload/', methods=['POST'])
def upload():
    setname = request.form.get('filename')
    imagefile = request.files.get('imagefile', '')
        
    # save locally temporarily to convert from dicom to jpg format
    tempsaved = 'temp/'
    if not path.exists(tempsaved):
        makedirs(tempsaved)
    imagefile.save(tempsaved+setname)
    im_list = subprocess.call(['mogrify', '-format', 'jpg', tempsaved+setname])
    num_images = len(fnmatch.filter(listdir(tempsaved), '*.jpg'))


    # save as blob to database
    # return image id and number of images in set
    return render_template('submit.html', title='DICOM Viewer')

# handles getting jpg files from a set in database to be rendered in browser
@app.route('/api/upload/<int:img_id>', methods=['GET'])
def get_image(img_id):
    try:
        #get image set from database
       filename = 'images/IM_0011-'+ str(img_id) + '.jpg'
       return send_file(filename)
    except:
       filename = 'images/error.gif'
       return send_file(filename)

#TODO make this page auto routed to from the "/" page
#use test person Admin, pass: admin for now, added this into users table in database
#such as: http://127.0.0.1:5000/api/authenticate?name=Admin&password=admin 
@app.route("/api/authenticate")
def Authenticate():
    username = request.args.get('name')
    password = request.args.get('password')
    
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password, salt from users where name = %s", (username))
    
    #salt = uuid.uuid4().hex ## will need this to create accounts at some point

    data = cursor.fetchone()
    print data
    if data is None:
        return "Username or Password is wrong"
    else:
        salt = data[1]
        hashed_password = hashlib.sha512(password + salt).hexdigest()
        if data[0] == hashed_password:
            return "Logged in successfully"
        else:
            return "Username or Password is wrong"

if __name__ == '__main__':
    host="localhost",
    port=int("8080")
    app.run(debug=True)
