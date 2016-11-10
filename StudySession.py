from flask import g
import json

class StudySession:

    @staticmethod
    def newFromId(id):
        try:
            cursor = g.db.cursor()
            cursor.execute(                                                      
                "SELECT id, set_id, user_id, name, color, study_id FROM sessions "
                "WHERE id = %s", (id)
            )
            (id, set_id, user_id, name, color, study_id) = cursor.fetchone()
            return StudySession(id, set_id, user_id, name, color, study_id)
        except:
            return StudySession()

    @staticmethod
    def getAll(set_id="%", study_id="%"):
        try:
            cursor = g.db.cursor()
            cursor.execute(                                                      
                "SELECT id, set_id, user_id, name, color, study_id FROM sessions "
                "WHERE set_id LIKE %s AND study_id LIKE %s", (set_id, study_id)
            )
            data = cursor.fetchall()
            sessions = []
            for row in data:
                (id, set_id, user_id, name, color, study_id) = row
                sessions.append(StudySession(id, set_id, user_id, name, color, study_id))
            return sessions
        except:
            return []

    def __init__(self, id=None, set_id=None, user_id=None, name=None, color=None, study_id=None):
        self.id = id
        self.set_id = set_id
        self.user_id = user_id
        self.name = name
        self.color = color
        self.study_id = study_id
        
    def toJSON(self):
        return json.dumps(self.__dict__)
        
    def create(self):
        cursor = g.db.cursor()
        cursor.execute(                                                      
            "INSERT INTO sessions (set_id, user_id, name, color, study_id) "
            "VALUES (%s, %s, %s, %s, %s)", (self.set_id, self.user_id, self.name, self.color, self.study_id)
        )
        self.id = cursor.lastrowid
        
    def update(self):
        cursor = g.db.cursor()
        cursor.execute(
            "UPDATE sessions SET "
            "set_id = %s, "
            "user_id = %s, "
            "name = %s, "
            "color = %s, "
            "study_id = %s "
            "WHERE id = %s", (self.set_id, self.user_id, self.name, self.color, self.study_id, self.id)
        )
        
    def delete(self):
        cursor = g.db.cursor()
        cursor.execute(
            "DELETE FROM sessions "
            "WHERE id = %s", (self.id)
        )
        self.id = None
        
