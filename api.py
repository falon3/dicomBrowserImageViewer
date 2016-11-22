from Study import *
from ImageSet import *
from User import *
from Point import *
from Line import *
from json import *
from utils import *
from StudySession import *
from flask import Flask, session, abort, send_file, render_template, request, url_for, redirect, make_response, g

# API Routes #
# called from app.py

#@app.route("/api/point", methods=['POST'])
#@app.route("/api/point/<int:point_id>", methods=['GET', 'PUT', 'DELETE'])
#@login_required
def apiPoint(point_id=None):
    if(request.method == 'POST'):
        point = Point(line_id = request.json.get('line_id'), 
                      x = request.json.get('x'), 
                      y = request.json.get('y'), 
                      interpolated = 0)
        point.create()
    elif(request.method == 'PUT'):
        point = Point.newFromId(point_id)
        point.y = request.json.get('y')
        point.x = request.json.get('x')
        point.interpolated = 0
        point.update()
    elif(request.method == 'DELETE'):
        point = Point.newFromId(point_id)
        point.delete()
    elif(request.method == 'GET'):
        point = Point.newFromId(point_id)
    response = make_response(point.toJSON())
    response.headers['Content-Type'] = 'application/json'
    return response
    
#@app.route("/api/line", methods=['POST'])
#@app.route("/api/line/<int:line_id>", methods=['GET', 'DELETE'])
#@login_required
def apiLine(line_id=None):
    if(request.method == 'POST'):
        line = Line(image_id = request.json.get('image_id'), 
                    session_id = request.json.get('session_id'), 
                    color = request.json.get('color'))
        line.create()
    elif(request.method == 'DELETE'):
        line = Line.newFromId(line_id)
        line.delete()
    elif(request.method == 'GET'):
        line = Line.newFromId(line_id)
    response = make_response(line.toJSON())
    response.headers['Content-Type'] = 'application/json'
    return response
    
#@app.route("/api/session", methods=['POST'])
#@app.route("/api/session/<int:session_id>", methods=['GET', 'DELETE'])
#@login_required
def apiSession(session_id=None):
    if(request.method == 'POST'):
        imageset = ImageSet.newFromId(request.json.get('set_id'))
        study = Study.newFromName(imageset.study)
        sessions = StudySession.getAll(imageset.id, study.id)
        if(len(sessions) < study.num_sessions):
            s = StudySession(set_id = imageset.id, 
                             user_id = g.currentUser.userID,
                             name = str(g.currentUser.name) + "." + str(imageset.name) + "." + str(study.name) + "-" + str(len(sessions)),
                             color = request.json.get('color'),
                             study_id = study.id)
            s.create()
        else:
            s = StudySession()
    elif(request.method == 'DELETE'):
        s = StudySession.newFromId(session_id)
        s.delete()
    elif(request.method == 'GET'):
        s = StudySession.newFromId(session_id)
    response = make_response(s.toJSON())
    response.headers['Content-Type'] = 'application/json'
    return response

#@app.route("/api/sessions/<int:set_id>/points", methods=['GET'])
#@app.route("/api/sessions/<int:set_id>/<int:study_id>/points", methods=['GET'])
#@login_required
def apiPoints(set_id="%",study_id="%"):
    points = Point.getAll(set_id, study_id)
    response = make_response(json_encode_list(points))
    response.headers['Content-Type'] = 'application/json'
    return response
    
#@app.route("/api/sessions/<int:set_id>/lines", methods=['GET'])
#@app.route("/api/sessions/<int:set_id>/<int:study_id>/lines", methods=['GET'])
#@login_required
def apiLines(set_id="%",study_id="%"):
    lines = Line.getAll(set_id, study_id)
    response = make_response(json_encode_list(lines))
    response.headers['Content-Type'] = 'application/json'
    return response

#@app.route("/api/sessions/<int:set_id>", methods=['GET'])
#@app.route("/api/sessions/<int:set_id>/<int:study_id>", methods=['GET'])
#@login_required
def apiSessions(set_id="%",study_id="%"):
    s = StudySession.getAll(set_id, study_id)
    response = make_response(json_encode_list(s))
    response.headers['Content-Type'] = 'application/json'
    return response
