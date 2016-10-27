#!flask/bin/python
from flask import Flask, abort, send_file, render_template, request, url_for, redirect, make_response, g
from flaskext.mysql import MySQL
from functools import wraps
import hashlib, uuid
import subprocess
import fnmatch
import settings
from User import *
#import models
import glob
import datetime
from base64 import decodestring
from os import listdir, makedirs, path, remove
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
        checkCurrentUser()
        if not g.currentUser:
            return redirect('/authenticate')
        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        Logout()
    return decorated_function

@app.before_request
def before_request():
    g.db = mysql.connect()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.after_request
def after_request(response):
    if g.db is not None:
        g.db.commit()
        g.db.close()
        g.db = None
    print(response)
    return response

@app.route('/')
@login_required
def index():
    #return render_template('upload.html', title="Dicom Uploader")
    return redirect("/myimages/" + g.currentUser.name )

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
        return render_template('upload.html', error="Unable to convert image, needs a DICOM (.dcm) format")
    
    # get db connection cursor
    cursor = g.db.cursor()
         
    # create UNIQUE image set for this user and setname in database
    try:
        cursor.execute(                                                          
            "INSERT INTO image_sets (id, user_id, name)"                         
            "VALUES (NULL, %s, %s)", (g.currentUser.userID, setname)  
        )
    except Exception as e:
        err = e[1]
        if "Duplicate" in err:
            err = "Image set name already used for this user"
        # empty the temp files dir and return error message
        for img in glob.glob(tempsaved+setname+'*'):
            remove(img)
        return render_template('upload.html', error=err)
            
                                                                       
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
        if set_size > 2:
            remove(picture) # delete temp files
        
    remove(tempsaved+setname) # delete original
    # return image id and number of images in set
    return redirect("/viewset/"+str(current_setid), code=302)
    
# gets image set details from database to pass to template
@app.route('/viewset/<int:set_id>', methods=['GET'])
@login_required
def query_set(set_id):

    # get db connection cursor
    cursor = g.db.cursor()
    cursor.execute("SELECT id FROM images WHERE set_id='%s'", set_id)    
    img_list = cursor.fetchall()
    first = img_list[0][0]
    size = len(img_list)
    cursor.execute("SELECT name FROM image_sets WHERE id='%s'", set_id)
    set_name = cursor.fetchone()[0]
    print(set_name)
    
    return render_template('submit.html', title=set_name, first = first, size = size)
    
@app.route('/upload/<int:img_id>', methods=['GET'])
@login_required
def get_image(img_id):
    # get db connection cursor
    cursor = g.db.cursor()   
    try:
        #get image set from database
        cursor.execute("SELECT image FROM images WHERE id='%s'", img_id)        
        img = cursor.fetchone()[0]
        return send_file(BytesIO(img), mimetype='image/jpg')

    except:
        filename = 'images/error.gif'
        return send_file(filename)

@app.route("/authenticate/", methods=['GET', 'POST'])
def Authenticate():
    checkCurrentUser()
    
    if g.currentUser != None:
        # Already logged in!
        return redirect("/")

    username = request.form.get('username')
    password = request.form.get('password')
    
    if(username is None and password is None):
        return render_template('login.html', title='Login')

    # get db connection cursor
    cursor = g.db.cursor()
    
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
            # to further bolster security 
            response.set_cookie('username', username)
            response.set_cookie('password', hashed_password)
            return response
        else:
            return render_template('login.html', title='Login', error="Incorrect Username or Password")
            
    except:
        return render_template('login.html', title='Login', error="Incorrect Username or Password")


@app.route("/myimages/<username>/", methods=['GET'])
@login_required
def displayUserImageSets(username):
    cursor = g.db.cursor()
    cursor.execute("SELECT name from image_sets where user_id = %s", (g.currentUser.userID))
    data = cursor.fetchall()
    img_sets = [str(set[0]) for set in data]
    print(img_sets)
    
    
    return render_template('userpictures.html', title='User Image Set Library', result = img_sets)
    
            

@app.route("/newaccount/", methods=['GET', 'POST'])
def newUser():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    if(username is None or password is None or email is None):
        return render_template('newaccount.html', title='New User Registration')
    
    try:
        g.currentUser = User(username, password, email)
        print("HERE!")
        print(g.currentUser.name, g.currentUser.password)
        # to do check if valid and store in database
        # validate cookies and set current
    except Exception as e:
        print("USER not saved into db: " + str(e))
        err = e[1]
        err_entry = err.split()[2]
        if "Duplicate" in err and "name" in err:
            err = "Username " + err_entry + " already exists!"

        if "Duplicate" in err and "email" in err:
            err = "Email address " + err_entry + " is already used for another account!"
        return render_template('newaccount.html', title='NewAccount', error=err)

    response = make_response(redirect("/"))
    response.set_cookie('username', username)
    response.set_cookie('password', g.currentUser.password)
    return response
            
@app.route("/logout/")
def Logout():
    expire_date = datetime.datetime.now()
    expire_date = expire_date + datetime.timedelta(days=-30)
    response = make_response(redirect("/"))
    # TODO: Might add user auth tokens instead of storing the hashed password in the cookie
    # to further bolster security 
    response.set_cookie('username', '', expires=expire_date)
    response.set_cookie('password', '', expires=expire_date)
    g.currentUser = None
    return response

if __name__ == '__main__':
    
    app.run(debug=True, port=8080)
