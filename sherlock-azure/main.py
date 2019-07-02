from importlib import import_module
import os
from flask import Flask, render_template, Response, send_file
import cognitive_face as cf

from whatdoyousee import *

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from io import BytesIO
from PIL import Image
from time import sleep
from datetime import datetime
import logging
from flask_ask import Ask, statement, question
import base64
    
from camera_pi import Camera
camera = Camera()

key = '41c640b5a5ed45699e0797a76c7af4be'
cf.Key.set(key)
base_url = 'https://westus.api.cognitive.microsoft.com/face/v1.0/'
cf.BaseUrl.set(base_url)

image_file = 'image_file.png'

app = Flask(__name__)
ask = Ask(app, "/")

log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def alexa_launch():
    return question('Sherlock is hot, How can I help you?')

@ask.intent('AddFace')
def alexa_AddFace(FirstName):
    AddFace("{}".format(FirstName))
    response = "OK. I will remember {}".format(FirstName)
    return statement(response)

@ask.intent('Selfie')
def alexa_Selfie():
    Selfie() 
    response_txt = "Your selfie was taken and will be emailed"
    return statement(response_txt)

@ask.intent('WhoDoYouSee')
def alexa_WhoDoYouSee():
    response = "no response"
    response = "I see {}".format(IdentifyFace())
    return statement(response)

@ask.intent('WhatDoYouSee')
def alexa_whatsee():
    response = "no response"
    response = what_see(True)
    return statement(response)
 
@ask.session_ended
def session_ended():
    return "{}", 200

@ask.on_session_started
def new_session():
    log.info('new session started')
    
@app.route('/')
def index():
    print ("index page")
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/what_see')
def what_see(alexa=False):
    body = camera.get_frame()
    parsedText = WhatDoYouSee(body)
    imageFile_png = base64.b64encode(body).decode('ascii')  
    if alexa:
        return parsedText
    else:
        return render_template("what_see.html", what_see = parsedText, what_see_image = imageFile_png)

def Selfie():
    body = camera.get_frame() 
    response_txt = EmailHandler(body)
    return (response_txt)

def IdentifyFace():
    image = '/home/pi/ece498iot/lab4/sherlock-azure/faces/Detection_%s.png' %(datetime.now().strftime('%Y%m%d_%H%M%S'))
    with open(image, 'wb') as f:
        f.write(camera.get_frame())
        f.close()
    detect_responses = cf.face.detect(image)
    if len(detect_responses) == 0:
        return 'I see no one'
    face_id_list = []
    for faces in detect_responses:
        face_id = faces['faceId']
        print(face_id)
        face_id_list.append(face_id)
    identify_responses = cf.face.identify(face_id_list, 'my_friends')
    for person in cf.person.lists('my_friends'):
        identified = identify_responses[0]['candidates'][0]
        if person['personId'] == identified['personId']:
            responses = cf.person.add_face(image, 'my_friends', person['personId'])
            responses = cf.person_group.train('my_friends')
            identified_name = person['name']
            print(identified_name)
            break
    return identified_name
    
def AddFace(name):
    person_list = cf.person.lists('my_friends')
    if all(dic['name'] != name for dic in person_list):
        responses = cf.person.create('my_friends', name)
        person_id = responses['personId']
        print('Added {}'.format(person_id))
    else:
        for dic in person_list:
            if dic['name'] == name:
                person_id = dic['personId']
                break
    for num in range(5):
        image = '/home/pi/ece498iot/lab4/sherlock-azure/faces/%s.png' %(name)
        with open(image, 'wb') as f:
            f.write(camera.get_frame())
            f.close()
        sleep(0.1)
        responses = cf.person.add_face(image, 'my_friends', person_id)
        print('Adding Image %d..%s' %(num, responses))
    responses = cf.person.lists('my_friends')
    print('Get list ..%s' %(responses))
    responses = cf.person_group.train('my_friends')
    print('Training %s' %(responses))

def EmailHandler(body):
    if body != None:
        with open(image_file, 'wb') as f:
            f.write(body)
            f.close()

        see_txt = WhatDoYouSee(body)
        print ("see_txt=%s"% see_txt)
        
        if len(see_txt) > 0:
            fromAddr = '915slynn@gmail.com'
            toAddr = 'jpan22@illinois.edu'
            email_pwd = 'Aperture'
            SendEmail(fromAddr, toAddr, email_pwd, "Sherlock Selfie", see_txt, image_file)
            response_txt = "Selfie taken and email sent successfully"
            img = Image.open(BytesIO(body))
            img.show(title=see_txt)
        else:
            response_txt = "There was a problem taking the selfie."
    return response_txt

def SendEmail(fromAddr, toAddr, email_pwd, subject, body, attachFile=None):
    msg = MIMEMultipart()
    msg["From"] = fromAddr
    msg["To"] = toAddr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    if attachFile != None:
        attachment = open(attachFile, 'rb')
    
        part = MIMEBase("application", "octet-stream")
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachFile))
        msg.attach(part)
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(fromAddr, email_pwd)
        text = msg.as_string()
        
        server.sendmail(fromAddr, toAddr, text)
        server.quit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
