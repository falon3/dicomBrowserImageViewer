from flask import g
from Study import *
from Image import *
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
        
    def getStudy(self):
        return Study.newFromName(self.study)
        
    def getImages(self):
        # Should be rafactored into a getAll function in Image.py
        cursor = g.db.cursor()
        cursor.execute("SELECT i.id "
                       "FROM images i, image_sets s "
                       "WHERE i.set_id=%s "
                       "AND i.set_id = s.id "
                       "AND s.user_id=%s", (self.id, g.currentUser.userID))
        data = cursor.fetchall()
        imgs = list()
        for img in data:
            imgs.append(Image.newFromId(img[0]))
        return imgs
        
    def toJSON(self):
        return json.dumps(self.__dict__)
        
    def create(self):
        cursor = g.db.cursor()
        cursor.execute(                                                      
            "INSERT INTO image_sets (user_id, name, study) "
            "VALUES (%s, %s, %s)", (self.user_id, self.name, self.study)
        )
        self.id = cursor.lastrowid
        
    def update(self):
        cursor = g.db.cursor()
        cursor.execute(
            "UPDATE image_sets SET "
            "user_id = %s, "
            "name = %s, "
            "study = %s, "
            "WHERE id = %s", (self.user_id, self.name, self.study, self.id)
        )
        
    def delete(self):
        cursor = g.db.cursor()
        cursor.execute(
            "DELETE FROM image_sets "
            "WHERE id = %s", (self.id)
        )
        self.id = None
        
