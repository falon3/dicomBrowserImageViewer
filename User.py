from flask import Flask, g, request
import hashlib, uuid

class User:

    def __init__(self, username, password, email, userID= None):
        self.name = username
        self.email = email
        self.password = password

        if userID:
            self.userID = userID

        else:
            self.storeUserInDB()

    def storeUserInDB(self):
        '''creates userid and hashed, salted password and stores in database'''

        salt = uuid.uuid4().hex # password salt
        print(type(salt))
        hashed_password = hashlib.sha512(self.password + salt).hexdigest()
        self.password = hashed_password

        # get db connection cursor
        cursor = g.db.cursor()
        cursor.execute(                                                      
            "INSERT INTO users (id, name, password, salt, email)"
            "VALUES (NULL, %s, %s, %s, %s)", (self.name, hashed_password, salt, self.email)           
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
        print(userID)
        return userID[0]
        

# check to make sure no one has manually changed the cookies
def checkCurrentUser():
    # get user info from cookies 
    username = request.cookies.get('username')
    hashed_password = request.cookies.get('password')
    g.currentUser = None
    if(username is None):
        username = ""
    if(hashed_password is None):
        hashed_password = ""

    # check if cookies match database entry
    cursor = g.db.cursor()
    cursor.execute("SELECT password FROM users WHERE name = %s", (username))
    stored_psswd = cursor.fetchone()
    if stored_psswd is None:
        g.currentUser = None
    else:
        if stored_psswd[0] == hashed_password:
            # This is a legit user
            cursor.execute("SELECT name, email, id FROM users WHERE name = %s", (username))
            data = cursor.fetchone()
            g.currentUser = User(data[0], hashed_password, data[1], data[2])
        else:
            g.currentUser = None
            

    
