from flask import g
import json

class Line:

    @staticmethod
    def newFromId(id):
        try:
            cursor = g.db.cursor()
            cursor.execute(                                                      
                "SELECT `id`, `image_id`, `session_id`, `color` FROM `lines` "
                "WHERE `id` = %s", (id)
            )
            (id, image_id, session_id, color) = cursor.fetchone()
            return Line(id, image_id, session_id, color)
        except:
            return Line()

    @staticmethod
    def getAll(set_id="%", study_id="%"):
        try:
            cursor = g.db.cursor()
            cursor.execute(                                                      
                "SELECT l.`id`, l.`image_id`, l.`session_id`, l.`color` FROM `sessions` s, `lines` l "
                "WHERE s.id = l.session_id "
                "AND   s.set_id LIKE %s AND s.study_id LIKE %s", (set_id, study_id)
            )
            data = cursor.fetchall()
            lines = []
            for row in data:
                (id, image_id, session_id, color) = row
                lines.append(Line(id, image_id, session_id, color))
            return lines
        except Exception as e:
            print e
            return []

    def __init__(self, id=None, image_id=None, session_id=None, color=None):
        self.id = id
        self.image_id = image_id
        self.session_id = session_id
        self.color = color
        
    def toJSON(self):
        return json.dumps(self.__dict__)
        
    def create(self):
        cursor = g.db.cursor()
        cursor.execute(                                                      
            "INSERT INTO `lines` (`image_id`, `session_id`, `color`) "
            "VALUES (%s, %s, %s)", (self.image_id, self.session_id, self.color)           
        )
        self.id = cursor.lastrowid
        
    def update(self):
        cursor = g.db.cursor()
        cursor.execute(
            "UPDATE `lines` SET "
            "`image_id` = %s, "
            "`session_id` = %s, "
            "`color` = %s, "
            "WHERE `id` = %s", (self.image_id, self.session_id, self.color, self.id)
        )
        
    def delete(self):
        cursor = g.db.cursor()
        cursor.execute(
            "DELETE FROM `lines` "
            "WHERE `id` = %s", (self.id)
        )
        self.id = None
        
