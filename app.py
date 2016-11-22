#!flask/bin/python
from flask import Flask, session, abort, send_file, render_template, request, url_for, redirect, make_response, g
from flaskext.mysql import MySQL
from flask_session import Session
from flask_compress import Compress
from functools import wraps
import hashlib, uuid
import subprocess
import fnmatch
import settings
import re
import api
from utils import *
from User import *
from Point import *
from Line import *
from StudySession import *
from Study import *
from ImageSet import *
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
Compress(app)

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

''' 
home dashboard of pictures
    # Techs only see what they uploaded, 
    # participants only see what belongs to a study
    # researchers see all'''
@app.route('/')
@login_required
def index(err=''):
    setname = request.args.get("search")
    if not setname:
        setname = ''

    user_id = "LIKE '%'"
    
    cursor = g.db.cursor()
    # get all image set info to be displayed in table
    qbuilder = "SELECT s.name, s.id, s.created_on, MIN(i.id) as start, s.study, COUNT(*) FROM image_sets s, images i WHERE i.set_id = s.id  "

    param = None
    if g.currentUser.acctype == 'Tech':
        qbuilder += "AND user_id = %s "
        param = g.currentUser.userID
    elif g.currentUser.acctype == 'Participant':
        qbuilder += "AND s.study IS NOT NULL "
    qbuilder+= "GROUP BY s.id"

    if param:
        cursor.execute(qbuilder, (param))
    else:
        cursor.execute(qbuilder)
    data = cursor.fetchall()
    img_dict = {str(set[0]): {'id':set[1], 'timestamp': set[2], 'start': set[3], 'mid': int(set[3] + set[5]/2), 'study': set[4] } for set in data}

    # count how many DICOMS in same prefixed studyname
    cursor.execute("Select DISTINCT LEFT(i.name, INSTR(i.name,'-')-1), count(*) "
                   "FROM image_sets i, image_sets n "
                   "WHERE LEFT(i.name,INSTR(i.name,'-')-1) = LEFT(n.name,INSTR(n.name,'-')-1) "
                   "GROUP BY i.name")
    counts = cursor.fetchall()
    count_dict = {str(base[0]): base[1] for base in counts}
    for key in img_dict:
        img_dict[key]['count'] = count_dict[key.split('-')[0]]

    all_studies = Study.getAllNames()
        
    return render_template('userpictures.html', title='Images', result = img_dict, setname=setname, studies = all_studies, error=err)    

# STUDIES ROUTES
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

    # create UNIQUE image set for this user and setname in database
    study = Study(name = name, num_sessions = sessions, user_id = g.currentUser.userID)
    try:
        study.create()
    except Exception as e:
        err = e[1]
        if "Duplicate" in err:
            err = "Study name already Exists!"
        return new_study(err)
            
    return display_studies()

@app.route('/studies/', methods=['GET'])
@login_required
def display_studies(error=''):
    if (g.currentUser.acctype == 'Tech'):
        return redirect('/') # Techs don't need access to studies

    cursor = g.db.cursor()
    cursor.execute("SELECT s.name, s.id, s.created_on, num_sessions, u.name, COUNT(i.id)  "
                   "FROM users u, studies s LEFT JOIN image_sets i ON study = s.name "
                   "WHERE s.user_id = u.id "
                   "GROUP BY s.id")
    data = cursor.fetchall()
    study_dict = {str(study[0]): {'id': study[1], 'created_on': study[2], 'num_sessions': study[3], 'creator': study[4], 'count':study[5] } for study in data}

    return render_template('studies.html', title='Studies', error=error, result = study_dict)  

@app.route('/studies/<name>', methods=['GET'])
@login_required
def expand_study(name):
     cursor = g.db.cursor()
     cursor.execute("SELECT i.name, i.id, i.created_on, COUNT(*), MIN(im.id) as start "
                    "FROM image_sets i, images im "
                    "WHERE i.study = %s "
                    "AND im.set_id = i.id "
                    "AND i.study IS NOT NULL "
                    "GROUP BY i.name", (name))
     data = cursor.fetchall()
     img_dict = {str(dcm[0]): {'id':dcm[1], 'timestamp': str(dcm[2]), 'index': int(dcm[4] + dcm[3]/2) } for dcm in data}
     response = make_response(json.dumps(img_dict))
     response.headers['Content-Type'] = 'application/json'
     return response

# handle deleting studies here (only for researchers)
@app.route('/studies/<name>', methods=['DELETE'])
@login_required    
def delete_study(name):
    if (g.currentUser.acctype != 'Researcher'):
        err = "You don't have permissions to remove studies"
        return display_studies(err)

    study = Study.newFromName(name)
    study.delete()
    response = make_response(json.dumps({'success': True}))
    response.headers['Content-Type'] = 'application/json'
    return response

# IMAGE SET routes #
# handle deleting image_sets from studies template here (only for researchers)
@app.route('/imgSet/<int:set_id>', methods=['DELETE'])
@login_required    
def delete_DICOM(set_id):
    if (g.currentUser.acctype != 'Researcher'):
        err = "You don't have permissions to remove studies"
        return display_studies(err)

    try:
        im_set = ImageSet.newFromId(set_id)
        im_set.delete()
        response = make_response(json.dumps({'success': True}))
        response.headers['Content-Type'] = 'application/json'
    except Exception as e:
        response = make_response(json.dumps({'success': False}))
        response.headers['Content-Type'] = 'application/json'

    return response

# gets image set details from database to pass to template
@app.route('/viewset/<int:set_id>:<name>', methods=['GET'])
@login_required
def query_set(set_id, name):
    if (g.currentUser.acctype == 'Tech'):
        return redirect('/')
    imageset = ImageSet.newFromId(set_id)
    imgs = imageset.getImages()
    first = imgs[0].id
    size = len(imgs)
    return render_template('viewer.html', title = imageset.name, imageset=imageset, first = first, size = size)

# UPLOAD routes#
@app.route('/upload/', methods=['GET'])
@login_required
def load_upload_page(error=''):
    if (g.currentUser.acctype == 'Participant'):
        err = "You don't have permissions to upload"
        return index(err)
    study_select = request.args.get('study')
    studies = Study.getAllNames()
    if study_select not in studies:
        study_select = ''
    return render_template('upload.html', title= "Upload Dicom", studies = studies, error=error, study_select = study_select)

# handles uploading Dicom files, converting into jpg format and storing into database
@app.route('/upload/', methods=['POST'])
@login_required
def upload():
    if (g.currentUser.acctype == 'Participant'):
        err = "You don't have permissions to upload"
        return index(err)
    setname = request.form.get('filename')
    setname = re.sub('[^A-Za-z0-9]+', '', setname)
    imagefiles = request.files.getlist('imagefile')
    study = request.form.get('study')    

    for dicom in imagefiles:
        fullname = setname + '-' + str(dicom.filename.strip('.dcm'))
        # save locally temp to convert from dicom to jpg format
        tempsaved = path.dirname(path.realpath(__file__)) + '/temp/'
        if not path.exists(tempsaved):
            makedirs(tempsaved)

        dicom.save(tempsaved+fullname)    
        try:
            output = subprocess.check_output(['identify', '-format', '%[dcm:PixelSpacing],', str(tempsaved+fullname)])
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
    
        convert = subprocess.call(['mogrify', '-resize', resize, '-format', 'jpg', tempsaved+fullname])
        set_size = len(fnmatch.filter(listdir(tempsaved), '*.jpg'))
        if convert != 0:
            return load_upload_page(error="Unable to convert image, needs a DICOM (.dcm) format")
    
        # create UNIQUE image set for this user and setname in database
        imageset = ImageSet(user_id = g.currentUser.userID, name = fullname, study = study)
        try:
            imageset.create()
        except Exception as e:
            err = e[1]
            if "Duplicate" in err:
                err = "Image set name and DICOM already used for this user"
            # empty the temp files dir and return error message
            for img in glob.glob(tempsaved+fullname+'*'):
                remove(img)
            return load_upload_page(error=err)

        # save all in set as blobs in images table in database in correct order
        for index in range(set_size):
            if(set_size > 1):
                picture = tempsaved + fullname + "-" + str(index) + ".jpg"
            else:
                picture = tempsaved + fullname + ".jpg"
            picture = path.abspath(picture)
            contents = file_get_contents(picture)

            image = Image(set_id = imageset.id, image = contents)
            image.create()
            if set_size > 2:
                remove(picture) # delete temp files
        
        remove(tempsaved+fullname) # delete original

    return redirect("/"+ "?search=" + setname , code=302)  

#get image set from database
@app.route('/upload/<int:img_id>', methods=['GET'])
@login_required
def get_image(img_id):
    try:
        img = Image.newFromId(img_id, includeImage=True)
        return send_file(BytesIO(img.image), mimetype='image/jpg')
    except:
        filename = 'images/error.gif'
        return send_file(filename)

# login and account routes #
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
    return api.apiPoint(point_id)
    
@app.route("/api/line", methods=['POST'])
@app.route("/api/line/<int:line_id>", methods=['GET', 'DELETE'])
@login_required
def apiLine(line_id = None):
    return api.apiLine(line_id)
    
@app.route("/api/session", methods=['POST'])
@app.route("/api/session/<int:session_id>", methods=['GET', 'DELETE'])
@login_required
def apiSession(session_id=None):
    return api.apiSession(session_id)

@app.route("/api/sessions/<int:set_id>/points", methods=['GET'])
@app.route("/api/sessions/<int:set_id>/<int:study_id>/points", methods=['GET'])
@login_required
def apiPoints(set_id="%",study_id="%"):
    return api.apiPoints(set_id,study_id)
    
@app.route("/api/sessions/<int:set_id>/lines", methods=['GET'])
@app.route("/api/sessions/<int:set_id>/<int:study_id>/lines", methods=['GET'])
@login_required
def apiLines(set_id="%",study_id="%"):
    return api.apiLines(set_id,study_id)

@app.route("/api/sessions/<int:set_id>", methods=['GET'])
@app.route("/api/sessions/<int:set_id>/<int:study_id>", methods=['GET'])
@login_required
def apiSessions(set_id="%",study_id="%"):
    return api.apiSessions(set_id,study_id)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
