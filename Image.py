from flask import g
import json

class Image:

    @staticmethod
    def newFromId(id, includeImage=False):
        try:
            cursor = g.db.cursor()
            if(includeImage):
                cursor.execute(
                    "SELECT id, set_id, image FROM images "
                    "WHERE id = %s", (id)
                )
            else:
                cursor.execute(
                    "SELECT id, set_id, '' as image FROM images "
                    "WHERE id = %s", (id)
                )
            (id, set_id, image) = cursor.fetchone()
            return Image(id, set_id, image)
        except:
            return Image()

    def __init__(self, id=None, set_id=None, image=None):
        self.id = id
        self.set_id = set_id
        self.image = image
        
    def toJSON(self):
        return json.dumps(self.__dict__)
        
    def create(self):
        cursor = g.db.cursor()
        cursor.execute(                                                      
            "INSERT INTO images (set_id, image) "
            "VALUES (%s, %s)", (self.set_id, self.image)
        )
        self.id = cursor.lastrowid
        
    def update(self):
        cursor = g.db.cursor()
        cursor.execute(
            "UPDATE images SET "
            "set_id = %s, "
            "image = %s, "
            "WHERE id = %s", (self.set_id, self.image, self.id)
        )
        
    def delete(self):
        cursor = g.db.cursor()
        cursor.execute(
            "DELETE FROM images "
            "WHERE id = %s", (self.id)
        )
        self.id = None
        
