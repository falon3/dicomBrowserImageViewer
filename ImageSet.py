from flask import g
import json

class ImageSet:

    @staticmethod
    def newFromId(id):
        try:
            cursor = g.db.cursor()
            cursor.execute(                                                      
                "SELECT id, user_id, name, created_on, study FROM image_sets "
                "WHERE id = %s", (id)
            )
            (id, user_id, name, created_on, study) = cursor.fetchone()
            return ImageSet(id, user_id, name, created_on, study)
        except:
            return ImageSet()

    def __init__(self, id=None, user_id=None, name=None, created_on=None, study=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.created_no = created_on
        self.study = study
        
    def toJSON(self):
        return json.dumps(self.__dict__)
        
    def create(self):
        cursor = g.db.cursor()
        cursor.execute(                                                      
            "INSERT INTO image_sets (user_id, name, created_on, study) "
            "VALUES (%s, %s, %s, %s)", (self.user_id, self.name, self.created_on, self.study)
        )
        self.id = cursor.lastrowid
        
    def update(self):
        cursor = g.db.cursor()
        cursor.execute(
            "UPDATE image_sets SET "
            "user_id = %s, "
            "name = %s, "
            "created_on = %s, "
            "study = %s, "
            "WHERE id = %s", (self.user_id, self.name, self.created_on, self.study, self.id)
        )
        
    def delete(self):
        cursor = g.db.cursor()
        cursor.execute(
            "DELETE FROM image_sets "
            "WHERE id = %s", (self.id)
        )
        self.id = None
        
