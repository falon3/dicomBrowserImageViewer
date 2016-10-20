#!flask/bin/python
from flask import Flask, abort, send_file, render_template, request, url_for, redirect, make_response, g
from flaskext.mysql import MySQL
from functools import wraps
import hashlib, uuid
import subprocess
import fnmatch
import settings
import glob
import datetime
from base64 import decodestring
from os import listdir, makedirs, path, remove
from base64 import decodestring
from io import BytesIO
import fnmatch

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = settings.database['user']
app.config['MYSQL_DATABASE_PASSWORD'] = settings.database['passwd']
app.config['MYSQL_DATABASE_DB'] = settings.database['db']
app.config['MYSQL_DATABASE_HOST'] = settings.database['host']
mysql.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = getLoggedInUser()
        if user is None:
            return redirect('/authenticate')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('upload.html', title='Upload DICOM')

# handles uploading Dicom files, converting into jpg format and storing into database
@app.route('/upload/', methods=['POST'])
@login_required
def upload():
    setname = request.form.get('filename')
    imagefile = request.files.get('imagefile', '')
        
    # save locally temp to convert from dicom to jpg format
    tempsaved = 'temp/'
    if not path.exists(tempsaved):
        makedirs(tempsaved)
    imagefile.save(tempsaved+setname)
    convert = subprocess.call(['mogrify', '-format', 'jpg', tempsaved+setname])
    set_size = len(fnmatch.filter(listdir(tempsaved), '*.jpg'))
    if convert != 0:
        return "Unable to convert image, press back and try a DICOM format"
    
    # make new db connection 
    conn = mysql.connect()
    cursor = conn.cursor()
         
    # get current logged in user id
    current_user = getLoggedInUser()                                               
    # create UNIQUE image set for this user and setname in database
    try:
        cursor.execute(                                                          
            "INSERT INTO image_sets (id, user_id, name)"                         
            "VALUES (NULL, %s, %s)", (current_user['id'], setname)                   
        )
    except:
        # empty the temp files dir and return error message
        for img in glob.glob(tempsaved+'*'):
            remove(img)
            return "Duplicate image set name for this user, press back and try again"
            
                                                                       
    # get current image_set id    
    
    cursor.execute("SELECT id FROM image_sets WHERE name='" + setname + "'") 
    current_setid = cursor.fetchone()[0]  
    
    # save all in set as blobs in images table in database in correct order
    for index in range(set_size):
        picture = tempsaved + setname + "-" + str(index) + ".jpg"
        picture = path.abspath(picture)
        subprocess.call(['chmod', '777', picture])

        cursor.execute(
            "INSERT INTO images (id, set_id, image)"
            "VALUES (NULL, %s, LOAD_FILE(%s))", (current_setid, picture) 
        )
        remove(picture) # delete temp files
        
    remove(tempsaved+setname) # delete temp directory
    conn.commit()
    conn.close()

    # return image id and number of images in set
    return redirect("/viewset/"+str(current_setid), code=302)
    
# gets image set details from database to pass to template
@app.route('/viewset/<int:set_id>', methods=['GET'])
@login_required
def query_set(set_id):
    # make new db connection 
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM images WHERE set_id='%s'", set_id)
    img_list = cursor.fetchall()
    first = img_list[0][0]
    size = len(img_list)
    
    return render_template('submit.html', title='DICOM Viewer', first = first, size = size)
    
@app.route('/upload/<int:img_id>', methods=['GET'])
@login_required
def get_image(img_id):
    # make new db connection 
    conn = mysql.connect()
    cursor = conn.cursor()    
    try:
        #get image set from database
        cursor.execute("SELECT image FROM images WHERE id='%s'", img_id)        
        img = cursor.fetchone()[0]
        return send_file(BytesIO(img), mimetype='image/jpg')
    except:
        filename = 'images/error.gif'
        return send_file(filename)

@app.route("/authenticate", methods=['GET', 'POST'])
def Authenticate():
    user = getLoggedInUser()
    
    if user != None:
        # Already logged in!
        return redirect("/")

    username = request.form.get('username')
    password = request.form.get('password')
    
    if(username is None and password is None):
        return render_template('login.html', title='Login')

    cursor = mysql.connect().cursor()
    
    # salt = uuid.uuid4().hex ## will need this to create accounts at some point
    # #print(salt)
    # hashed_password = hashlib.sha512(password + salt).hexdigest()
    # print("pass: ", hashed_password)
    # print("salt:", salt)

    try:
        cursor.execute("SELECT password, salt from users where name = %s", (username))
        passwd, salt = cursor.fetchone()
        hashed_password = hashlib.sha512(password + salt).hexdigest()
        
        if passwd == hashed_password:
            response = make_response(redirect("/"))
            # TODO: Might add user auth tokens instead of storing the hashed password in the cookie
            # to furthe bolster security 
            response.set_cookie('username', username)
            response.set_cookie('password', hashed_password)
            return response
        else:
            return render_template('login.html', title='Login', error="Incorrect Username or Password")
            
    except:
        return render_template('login.html', title='Login', error="Incorrect Username or Password")
            
            
@app.route("/logout")
def Logout():
    expire_date = datetime.datetime.now()
    expire_date = expire_date + datetime.timedelta(days=-30)
    response = make_response(redirect("/"))
    # TODO: Might add user auth tokens instead of storing the hashed password in the cookie
    # to furthe bolster security 
    response.set_cookie('username', '', expires=expire_date)
    response.set_cookie('password', '', expires=expire_date)
    return response

# Should be refactored into a new 'User' class
def getLoggedInUser():
    username = request.cookies.get('username')
    hashed_password = request.cookies.get('password')
    g.user = None
    if(username is None):
        username = ""
    if(hashed_password is None):
        hashed_password = ""

    # make new db connection 
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM users WHERE name = %s", (username))
    data = cursor.fetchone()
    if data is None:
        return None;
    else:
        if data[0] == hashed_password:
            # This is a legit user
            cursor.execute("SELECT id, name, email FROM users WHERE name = %s", (username))
            data = cursor.fetchone()
            g.user = dict(id = data[0],
                          name = data[1],
                          email = data[2])
            return g.user
        else:
            return None

if __name__ == '__main__':
    host="localhost",
    port=int("8080")
    app.run(debug=True)
