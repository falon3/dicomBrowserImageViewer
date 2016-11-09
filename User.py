from flask import Flask, session, g, request
import hashlib, uuid

class User:

    def __init__(self, username, password, email, acctype= None, userID= None):
        self.name = username
        self.email = email
        self.password = password
        self.acctype = acctype

        if userID:
            self.userID = userID
        else:
            self.storeUserInDB()

    def storeUserInDB(self):
        '''creates userid and hashed, salted password and stores in database'''

        salt = uuid.uuid4().hex # password salt
        hashed_password = hashlib.sha512(self.password + salt).hexdigest()
        self.password = hashed_password

        # get db connection cursor
        cursor = g.db.cursor()
        cursor.execute(                                                      
            "INSERT INTO users (name, password, salt, email, acctype)"
            "VALUES (%s, %s, %s, %s, %s)", (self.name, hashed_password, salt, self.email, self.acctype)           
        )
        self.userID = getIDbyUsername(self.name)

def getIDbyUsername(username):
    # get and store in object autocreated_userID
    cursor = g.db.cursor()
    cursor.execute("SELECT id FROM users WHERE name = %s", (username))
    userID = cursor.fetchone()
    if userID is None:
        return None
    else:
        return userID[0]
        

# check the current session
def checkCurrentUser():
    try:
        username = session['username']
        g.currentUser = None

        # get db connection cursor
        cursor = g.db.cursor()

        cursor.execute("SELECT name, email, acctype, id FROM users WHERE name = %s", (username))
        data = cursor.fetchone()
        g.currentUser = User(data[0], None, data[1], data[2], data[3])

    except Exception as e:
        g.currentUser = None
        
    
    return g.currentUser 
