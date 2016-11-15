from flask import g
import json

class Study:

    @staticmethod
    def newFromId(id):
        try:
            cursor = g.db.cursor()
            cursor.execute(                                                      
                "SELECT id, name, created_on, num_sessions, user_id FROM studies "
                "WHERE id = %s", (id)
            )
            (id, name, created_on, num_sessions, user_id) = cursor.fetchone()
            return Study(id, name, created_on, num_sessions, user_id)
        except:
            return Study()
            
    @staticmethod
    def newFromName(name):
        try:
            cursor = g.db.cursor()
            cursor.execute(                                                      
                "SELECT id, name, created_on, num_sessions, user_id FROM studies "
                "WHERE name = %s", (name)
            )
            (id, name, created_on, num_sessions, user_id) = cursor.fetchone()
            return Study(id, name, created_on, num_sessions, user_id)
        except:
            return Study()
            
    @staticmethod
    def getAll():
        try:
            cursor = g.db.cursor()
            cursor.execute("SELECT id, name, created_on, num_sessions, user_id FROM studies")
            data = cursor.fetchall()
            studies = []
            for row in data:
                (id, name, created_on, num_sessions, user_id) = row
                studies.append(Study(id, name, created_on, num_sessions, user_id))
            return studies
        except:
            return []

    def __init__(self, id=None, name=None, created_on=None, num_sessions=None, user_id=None):
        self.id = id
        self.name = name
        self.created_on = created_on
        self.num_sessions = num_sessions
        self.user_id = user_id
        
    def toJSON(self):
        return json.dumps(self.__dict__)
        
    def create(self):
        cursor = g.db.cursor()
        cursor.execute(                                                      
            "INSERT INTO studies (name, created_on, num_sessions, user_id) "
            "VALUES (%s, %s, %s, %s)", (self.name, self.created_on, self.num_sessions, self.user_id)
        )
        self.id = cursor.lastrowid
        
    def update(self):
        cursor = g.db.cursor()
        cursor.execute(
            "UPDATE studies SET "
            "name = %s, "
            "created_on = %s, "
            "num_sessions = %s, "
            "user_id = %s, "
            "WHERE id = %s", (self.name, self.created_on, self.num_sessions, self.user_id, self.id)
        )
        
    def delete(self):
        cursor = g.db.cursor()
        cursor.execute(
            "DELETE FROM studies "
            "WHERE id = %s", (self.id)
        )
        self.id = None
        
