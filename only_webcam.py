#!/usr/bin/env python
from datetime import datetime
from flask import Flask, render_template, Response, request
import numpy as np
import cv2
import wiringpi

OUTPUT = 1 # настройка пина на выход
PIN_TO_PWM_0 = 2 # 7 pin
PIN_TO_PWM_1 = 3 # 8 pin
FREQ_PWM = 500
wiringpi.wiringPiSetup()

# инитим пин на выход
wiringpi.pinMode(PIN_TO_PWM_0,OUTPUT)
wiringpi.pinMode(PIN_TO_PWM_1,OUTPUT)
# настрйока частоты работы ШИМ
#wiringpi.softPwmCreate(PIN_TO_PWM_0,0,FREQ_PWM)
#wiringpi.softPwmCreate(PIN_TO_PWM_1,0,FREQ_PWM)
#wiringpi.softPwmStop(PIN_TO_PWM_0)

#Initialize the Flask app
app = Flask(__name__)
#global pwm_az pwm_tilt
pwm_az = 0
pwm_tilt = 0

def gen_frames():
    global camera

    while True:
        success, frame = camera.read()  # read the camera frame
        if (camera.isOpened() == True):
            ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            print("no device webcam")

@app.route('/')
def index():
    global camera
    for i in range(5):
        print("/dev/video"+str(i))
        camera = cv2.VideoCapture("/dev/video"+str(i))
#        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
 #       camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if (camera.isOpened() == True):
            print("webcam open video"+str(i))
            break
        else:
            print("not open /dev/video"+str(i))

    return render_template('index.html')

@app.route('/login', methods=["POST","GET"])
def login():
    global pwm_az,pwm_tilt
    #wiringpi.softPwmCreate(PIN_TO_PWM_0,0,200)
    #wiringpi.softPwmCreate(PIN_TO_PWM_1,0,200)
    #wiringpi.delay(50)
    if request.method == "POST":
        wiringpi.softPwmCreate(PIN_TO_PWM_0,0,FREQ_PWM)
        wiringpi.softPwmCreate(PIN_TO_PWM_1,0,FREQ_PWM)
#       wiringpi.delay(200)
        h1 = request.form['red']
        if (pwm_az != int(h1)):
            pwm_az = int(h1)
            wiringpi.delay(100)
            wiringpi.softPwmWrite(PIN_TO_PWM_0,pwm_az)
            wiringpi.delay(100)
            wiringpi.softPwmStop(PIN_TO_PWM_0)
  #          wiringpi.delay(200)
       
        s1 = request.form['green']
        if (pwm_tilt != int(s1)):
            pwm_tilt = int(s1)
            wiringpi.delay(100)
            wiringpi.softPwmWrite(PIN_TO_PWM_1,pwm_tilt)
            wiringpi.delay(100)

            wiringpi.softPwmStop(PIN_TO_PWM_1)
     #       wiringpi.delay(200)
        print("az =",pwm_az," tilt=",pwm_tilt)
    else:
        print("Method = GET!")
        return ''
    return ''

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="192.168.0.124", port=8086, debug=True)
    #app.run(debug=True)
