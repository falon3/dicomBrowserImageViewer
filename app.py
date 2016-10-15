#!flask/bin/python
from flask import Flask, abort, send_file, render_template, request, url_for
from flaskext.mysql import MySQL
import subprocess
import fnmatch
import settings
import glob
from base64 import decodestring
from os import listdir, makedirs, path, remove

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USERS'] = settings.database['user']
app.config['MYSQL_DATABASE_PASSWORD'] = settings.database['passwd']
app.config['MYSQL_DATABASE_DB'] = settings.database['db']
app.config['MYSQL_DATABASE_HOST'] = settings.database['host']
mysql.init_app(app)
#mysql.connect(settings.database).autocommit(True)

@app.route('/api/')
def index():
    return render_template('upload.html', title='Upload DICOM')

# handles uploading Dicom files, converting into jpg format and storing into database
@app.route('/api/upload/', methods=['POST'])
def upload():
    setname = request.form.get('filename')
    imagefile = request.files.get('imagefile', '')
        
    # save locally temp to convert from dicom to jpg format
    tempsaved = 'temp/'
    if not path.exists(tempsaved):
        makedirs(tempsaved)
    imagefile.save(tempsaved+setname)
    convert = subprocess.call(['mogrify', '-format', 'jpg', tempsaved+setname])
    if convert != 0:
        return "Unable to convert image, press back and try a DICOM format"
    
    # make new db connection 
    conn = mysql.connect()
    cursor = conn.cursor()
         
    # get current logged in user id                                                                                
    cursor.execute("SELECT id FROM users WHERE isOnline='1'")                
    current_userid = cursor.fetchone()[0]                                    
                                                                             
    # create UNIQUE image set for this user and setname in database
    try:
        cursor.execute(                                                          
            "INSERT INTO image_sets (id, user_id, name)"                         
            "VALUES (NULL, %s, %s)", (current_userid, setname)                   
        )
    except:
        # empty the temp files dir and return error message
        for img in glob.glob(tempsaved+'*'):
            remove(img)
            return "Duplicate image set name for this user, press back and try again"
            
                                                                       
    # get current image_set id                                                  
    cursor.execute("SELECT id FROM image_sets WHERE name='" + setname + "'") 
    current_setid = cursor.fetchone()[0]  
    
    # save all in set as blobs in images table in database
    for picture in glob.glob(tempsaved+'*.jpg'):
        subprocess.call(['chmod', '777', picture])
        picture = path.abspath(picture)
        cursor.execute(
            "INSERT INTO images (id, set_id, image)"
            "VALUES (NULL, %s, LOAD_FILE(%s))", (current_setid, picture) 
        )
        remove(picture) # delete temp files
        
    remove(tempsaved+setname) # delete temp directory
    conn.commit()
    conn.close()

    # return image id and number of images in set
    return render_template('submit.html', title='DICOM Viewer', setID=current_setid )

# handles getting jpg files from a set in database to be rendered in browser
@app.route('/api/viewset/<int:set_id>', methods=['GET'])
def query_set(set_id):
    # make new db connection 
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM images WHERE set_id='%s'", set_id)
    img_set = cursor.fetchall()[0]

    #TODO: FIXXXXX THIS DOESN'T REALLY WORK YET
    counter = 0
    for img in img_set:
        f = open("temp"+str(counter)+".jpg","w")
        f.write(decodestring(img))
        f.close()
        counter+=1

    return send_file("temp0.jpg")
    conn.close()

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
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * from users where name='" + username + "' and password='" + password + "'")
    data = cursor.fetchone()
    if data is None:
        return "Username or Password is wrong"
    else:
        cursor.execute("UPDATE users SET isOnline='1' WHERE name='" + username + "' and password='" + password + "'")
        conn.commit()
        conn.close()
        return "Logged in successfully"

if __name__ == '__main__':
    host="localhost",
    port=int("8080")
    app.run(debug=True)
