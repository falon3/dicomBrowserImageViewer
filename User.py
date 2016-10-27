from flask import Flask, session, g, request

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
    try:
        username = session['username']
        g.currentUser = None

        # get db connection cursor
        cursor = g.db.cursor()

        cursor.execute("SELECT name, email, id FROM users WHERE name = %s", (username))
        data = cursor.fetchone()
        g.currentUser = User(data[0], None, data[1], data[2])
    except:
        g.currentUser = None
