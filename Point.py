from flask import g
import json

class Point:

    @staticmethod
    def newFromId(id):
        try:
            cursor = g.db.cursor()
            cursor.execute(                                                      
                "SELECT id, line_id, x, y, interpolated FROM points "
                "WHERE id = %s", (id)
            )
            (id, line_id, x, y, interpolated) = cursor.fetchone()
            return Point(id, line_id, x, y, interpolated)
        except:
            return Point()

    @staticmethod
    def getAll(set_id="%", study_id="%"):
        try:
            cursor = g.db.cursor()
            cursor.execute(                                                      
                "SELECT p.id, p.line_id, p.x, p.y, p.interpolated FROM `sessions` s, `lines` l, `points` p "
                "WHERE s.id = l.session_id "
                "AND   l.id = p.line_id "
                "AND   s.set_id LIKE %s AND s.study_id LIKE %s", (set_id, study_id)
            )
            data = cursor.fetchall()
            points = []
            for row in data:
                (id, line_id, x, y, interpolated) = row
                points.append(Point(id, line_id, x, y, interpolated))
            return points
        except:
            return []

    def __init__(self, id=None, line_id=None, x=0, y=0, interpolated=0):
        self.id = id
        self.line_id = line_id
        self.x = x
        self.y = y
        self.interpolated = interpolated
        
    def toJSON(self):
        return json.dumps(self.__dict__)
        
    def create(self):
        cursor = g.db.cursor()
        cursor.execute(                                                      
            "INSERT INTO points (line_id, x, y, interpolated) "
            "VALUES (%s, %s, %s, %s)", (self.line_id, self.x, self.y, self.interpolated)           
        )
        self.id = cursor.lastrowid
        
    def update(self):
        cursor = g.db.cursor()
        cursor.execute(
            "UPDATE points SET "
            "line_id = %s, "
            "x = %s, "
            "y = %s, "
            "interpolated = %s "
            "WHERE id = %s", (self.line_id, self.x, self.y, self.interpolated, self.id)
        )
        
    def delete(self):
        cursor = g.db.cursor()
        cursor.execute(
            "DELETE FROM points "
            "WHERE id = %s", (self.id)
        )
        self.id = None
        
