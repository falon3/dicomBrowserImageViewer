#!flask/bin/python
from flask import Flask, session, abort, send_file, render_template, request, url_for, redirect, make_response, g
from flaskext.mysql import MySQL
from flask_session import Session
from functools import wraps
import hashlib, uuid
import subprocess
import fnmatch
import settings
import re
from utils import *
from User import *
from Point import *
from Line import *
from StudySession import *
#import models
import glob
import datetime
from base64 import decodestring
from os import listdir, makedirs, path, remove, urandom, getcwd
from io import BytesIO
import fnmatch

mysql = MySQL()
app = Flask(__name__)
# DB Settings
app.config['MYSQL_DATABASE_USER'] = settings.database['user']
app.config['MYSQL_DATABASE_PASSWORD'] = settings.database['passwd']
app.config['MYSQL_DATABASE_DB'] = settings.database['db']
app.config['MYSQL_DATABASE_HOST'] = settings.database['host']
mysql.init_app(app)
# Session Settings
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = '/tmp/'
app.config.from_object(__name__)
app.permanent_session_lifetime = datetime.timedelta(hours=1)
Session(app)

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
        return f(*args, **kwargs)
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
    return response


@app.route('/')
@login_required
def index():
    cursor = g.db.cursor()
    cursor.execute("SELECT s.name, s.id, s.created_on, COUNT(*) as count, MIN(i.id) as start, s.study "
                   "FROM image_sets s, images i "
                   "WHERE user_id = %s "
                   "AND i.set_id = s.id "
                   "GROUP BY s.id", (g.currentUser.userID))
    data = cursor.fetchall()
    img_dict = {str(set[0]): {'id':set[1], 'timestamp': set[2], 'count': set[3], 'start': set[4], 'mid': int(set[4] + set[3]/2), 'study': set[5] } for set in data}
    return render_template('userpictures.html', title='my images', result = img_dict)    

@app.route('/studies/create/', methods=['GET'])
@login_required
def new_study(error=''):
    if (g.currentUser.acctype != 'Researcher'):
        return display_studies('insufficient permissions to create a study')
    return render_template('study_new.html', title='Studies', error=error)


@app.route('/studies/', methods=['POST'])
@login_required
def create_study():
    name = request.form.get('name')
    name = re.sub('[^A-Za-z0-9]+', '', name)
    sessions = request.form.get('sessions')

    # get db connection cursor
    cursor = g.db.cursor()
    # create UNIQUE image set for this user and setname in database
    try:
        cursor.execute(
            "insert into studies (id, name, created_on, num_sessions, user_id) "
            "VALUES (NULL, %s, NULL, %s, %s)", (name, sessions, g.currentUser.userID)             
        )
    except Exception as e:
        err = e[1]
        if "Duplicate" in err:
            err = "Study name already Exists!"
        return new_study(err)
            
    return display_studies()


@app.route('/studies/', methods=['GET'])
@login_required
def display_studies(error=''):
    cursor = g.db.cursor()
    cursor.execute("SELECT s.name, s.id, s.created_on, num_sessions, u.name  "
                   "FROM studies s, users u "
                   "WHERE s.user_id = u.id "
                   "GROUP BY s.id")
    data = cursor.fetchall()
    study_dict = {str(study[0]): {'id': study[1], 'created_on': study[2], 'num_sessions': study[3], 'creator': study[4] } for study in data}

    return render_template('studies.html', title='Studies', error=error, result = study_dict)    

@app.route('/upload/', methods=['GET'])
@login_required
def load_upload_page(error=''):
    cursor = g.db.cursor()
    cursor.execute("SELECT s.name FROM studies s GROUP BY s.id")
    data = cursor.fetchall()
    studies = [study[0] for study in data]
    return render_template('upload.html', title= "Upload Dicom", num_studies = len(studies), studies = studies, error=error)

# handles uploading Dicom files, converting into jpg format and storing into database
@app.route('/upload/', methods=['POST'])
@login_required
def upload():
    setname = request.form.get('filename')
    setname = re.sub('[^A-Za-z0-9]+', '', setname)
    imagefile = request.files.get('imagefile', '')
    study = request.form.get('study')
    
    #TODO: save study if not null into image_sets study column
  
    # save locally temp to convert from dicom to jpg format
    tempsaved = path.dirname(path.realpath(__file__)) + '/temp/'
    if not path.exists(tempsaved):
        makedirs(tempsaved)
    imagefile.save(tempsaved+setname)
    
    try:
        output = subprocess.check_output(['identify', '-format', '%[dcm:PixelSpacing],', str(tempsaved+setname)])
        matched_lines = [line for line in output.split(',')]
        rows, cols = matched_lines[0].strip().split('\\')
        rows = float(rows)
        cols = float(cols)
        
        resize = ""
        if(rows == cols):
            # no resize needed
            resize = "100%x100%"
        elif (cols > rows):
            factor = (cols/rows)*100
            resize = str(factor) + "%x100%"
        elif (rows > cols):
            factor = (rows/cols)*100
            resize = "100%x" + str(factor) + "%"
    except:
        resize = "100%x100%"
    
    convert = subprocess.call(['mogrify', '-resize', resize, '-format', 'jpg', tempsaved+setname])
    set_size = len(fnmatch.filter(listdir(tempsaved), '*.jpg'))
    if convert != 0:
        return load_upload_page(error="Unable to convert image, needs a DICOM (.dcm) format")
    
    # get db connection cursor
    cursor = g.db.cursor()
    # create UNIQUE image set for this user and setname in database
    try:
        cursor.execute(
            "INSERT INTO image_sets (user_id, name, study)"                      
            "VALUES (%s, %s, %s)", (g.currentUser.userID, setname, study)             
        )
    except Exception as e:
        err = e[1]
        if "Duplicate" in err:
            err = "Image set name already used for this user"
        # empty the temp files dir and return error message
        for img in glob.glob(tempsaved+setname+'*'):
            remove(img)
        return load_upload_page(error=err)
            
                                                                       
    # get current image_set id        
    cursor.execute("SELECT id FROM image_sets WHERE name='" + setname + "'") 
    current_setid = cursor.fetchone()[0]  
    
    # save all in set as blobs in images table in database in correct order
    for index in range(set_size):
        if(set_size > 1):
            picture = tempsaved + setname + "-" + str(index) + ".jpg"
        else:
            picture = tempsaved + setname + ".jpg"
        picture = path.abspath(picture)
        contents = file_get_contents(picture)

        cursor.execute(
            "INSERT INTO images (id, set_id, image)"
            "VALUES (NULL, %s, %s)", (current_setid, contents) 
        )
        if set_size > 2:
            remove(picture) # delete temp files
        
    remove(tempsaved+setname) # delete original
    return redirect("/viewset/"+ str(current_setid) +':'+ setname, code=302)
    
# gets image set details from database to pass to template
@app.route('/viewset/<int:set_id>:<name>', methods=['GET'])
@login_required
def query_set(set_id, name):

    # get db connection cursor
    cursor = g.db.cursor()
    cursor.execute("SELECT i.id "
                   "FROM images i, image_sets s "
                   "WHERE i.set_id=%s "
                   "AND i.set_id = s.id "
                   "AND s.user_id=%s", (set_id, g.currentUser.userID))    
    img_list = cursor.fetchall()
    first = img_list[0][0]
    size = len(img_list)
    cursor.execute("SELECT name "
                   "FROM image_sets "
                   "WHERE id=%s "
                   "AND user_id=%s", (set_id, g.currentUser.userID))
    set_name = cursor.fetchone()[0]

    return render_template('submit.html', title=set_name, set_id = set_id , first = first, size = size)
    
@app.route('/upload/<int:img_id>', methods=['GET'])
@login_required
def get_image(img_id):
    # get db connection cursor
    cursor = g.db.cursor()   
    try:
        #get image set from database
        cursor.execute("SELECT i.image "
                       "FROM images i, image_sets s "
                       "WHERE i.id=%s "
                       "AND i.set_id = s.id "
                       "AND s.user_id=%s", (img_id, g.currentUser.userID))        
        img = cursor.fetchone()[0]
        return send_file(BytesIO(img), mimetype='image/jpg')

    except:
        filename = 'images/error.gif'
        return send_file(filename)

@app.route("/authenticate/", methods=['GET', 'POST'])
def Authenticate():
    
    if checkCurrentUser() != None:
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
    err = "Incorrect Username or Password"
    try:
        cursor.execute("SELECT password, salt from users where name = %s", (username))
        passwd, salt = cursor.fetchone()
        hashed_password = hashlib.sha512(password + salt).hexdigest()
                
        if passwd == hashed_password:
            response = make_response(redirect("/"))
            session.clear()
            session['username'] = username
            if checkCurrentUser() == None:
                return render_template('login.html', title='Login', error= 'server error')
            return response
        else:
            return render_template('login.html', title='Login', error= err)
            
    except:
        return render_template('login.html', title='Login', error= err)

@app.route("/newaccount/", methods=['GET', 'POST'])
@logout_required
def newUser():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    acctype = request.form.get('type')

    # to handle GET
    if(username is None or password is None or email is None):
        return render_template('newaccount.html', title='New User Registration')
    
    try:
        g.currentUser = User(username, password, email, acctype)
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

    session.clear()
    session['username'] = username
    return redirect("/")
            
@app.route("/logout/")
def Logout():
    response = make_response(redirect("/"))
    session.clear()
    g.currentUser = None
    return response
    
# API Routes #
@app.route("/api/point", methods=['POST'])
@app.route("/api/point/<int:point_id>", methods=['GET', 'PUT', 'DELETE'])
@login_required
def apiPoint(point_id=None):
    if(request.method == 'POST'):
        point = Point(line_id = request.json.get('line_id'), 
                      x = request.json.get('x'), 
                      y = request.json.get('y'), 
                      interpolated = 0)
        point.create()
    elif(request.method == 'PUT'):
        point = Point.newFromId(point_id)
        point.y = request.json.get('y')
        point.x = request.json.get('x')
        point.interpolated = 0
        point.update()
    elif(request.method == 'DELETE'):
        point = Point.newFromId(point_id)
        point.delete()
    elif(request.method == 'GET'):
        point = Point.newFromId(point_id)
    response = make_response(point.toJSON())
    response.headers['Content-Type'] = 'application/json'
    return response
    
@app.route("/api/line", methods=['POST'])
@app.route("/api/line/<int:line_id>", methods=['GET', 'DELETE'])
@login_required
def apiLine(line_id=None):
    if(request.method == 'POST'):
        line = Line(image_id = request.json.get('image_id'), 
                    session_id = request.json.get('session_id'), 
                    color = request.json.get('color'))
        line.create()
    elif(request.method == 'DELETE'):
        line = Line.newFromId(line_id)
        line.delete()
    elif(request.method == 'GET'):
        line = Line.newFromId(line_id)
    response = make_response(line.toJSON())
    response.headers['Content-Type'] = 'application/json'
    return response
    
@app.route("/api/session", methods=['POST'])
@app.route("/api/session/<int:session_id>", methods=['GET', 'DELETE'])
@login_required
def apiSession(session_id=None):
    if(request.method == 'POST'):
        s = StudySession(set_id = request.json.get('set_id'), 
                         user_id = g.currentUser.userID,
                         name = request.json.get('name'),
                         color = request.json.get('color'),
                         study_id = request.json.get('study_id'))
        s.create()
    elif(request.method == 'DELETE'):
        s = StudySession.newFromId(session_id)
        s.delete()
    elif(request.method == 'GET'):
        s = StudySession.newFromId(session_id)
    response = make_response(s.toJSON())
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route("/api/sessions/<int:set_id>/points", methods=['GET'])
@app.route("/api/sessions/<int:set_id>/<int:study_id>/points", methods=['GET'])
@login_required
def apiPoints(set_id="%",study_id="%"):
    points = Point.getAll(set_id, study_id)
    response = make_response(json_encode_list(points))
    response.headers['Content-Type'] = 'application/json'
    return response
    
@app.route("/api/sessions/<int:set_id>/lines", methods=['GET'])
@app.route("/api/sessions/<int:set_id>/<int:study_id>/lines", methods=['GET'])
@login_required
def apiLines(set_id="%",study_id="%"):
    lines = Line.getAll(set_id, study_id)
    response = make_response(json_encode_list(lines))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route("/api/sessions/<int:set_id>", methods=['GET'])
@app.route("/api/sessions/<int:set_id>/<int:study_id>", methods=['GET'])
@login_required
def apiSessions(set_id="%",study_id="%"):
    s = StudySession.getAll(set_id, study_id)
    response = make_response(json_encode_list(s))
    response.headers['Content-Type'] = 'application/json'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=8080)
