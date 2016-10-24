from flask import Flask, g, request

class User:

    def __init__(self, username, password, email, userID= None):
        self.name = username
        self.password = password
        self.email = email

        if userID:
            self.userID = userID

        else:
            # store user in database
            pass

# check to make sure no one has manually changed the cookies
def checkCurrentUser():
    username = request.cookies.get('username')
    hashed_password = request.cookies.get('password')
    g.currentUser = None
    if(username is None):
        username = ""
        if(hashed_password is None):
            hashed_password = ""

    # get db connection cursor
    cursor = g.db.cursor()
    cursor.execute("SELECT password FROM users WHERE name = %s", (username))
    stored_psswd = cursor.fetchone()
    if stored_psswd is None:
        return None;
    else:
        if stored_psswd[0] == hashed_password:
            # This is a legit user
            cursor.execute("SELECT name, email, id FROM users WHERE name = %s", (username))
            data = cursor.fetchone()
            g.currentUser = User(data[0], hashed_password, data[1], data[2])
        else:
            g.currentUser = None
            

    
