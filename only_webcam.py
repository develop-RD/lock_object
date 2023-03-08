#!/usr/bin/env python
from datetime import datetime
from flask import Flask, render_template, Response, request
import numpy as np
import cv2
import wiringpi
from threading import Thread
import time

OUTPUT = 1 # настройка пина на выход
PIN_TO_PWM_0 = 2 # 7 pin
PIN_TO_PWM_1 = 3 # 8 pin
FREQ_PWM = 1200
wiringpi.wiringPiSetup()

# инитим пин на выход
wiringpi.pinMode(PIN_TO_PWM_0,OUTPUT)
wiringpi.pinMode(PIN_TO_PWM_1,OUTPUT)

#Initialize the Flask app
app = Flask(__name__)
#global pwm_az pwm_tilt
pwm_az = 0
pwm_tilt = 0

# финальный фрейм , который будет отправлен на сервак
global frame_end
frame_end = 0

# Функция захвата изображения и определения размеров объекта
def videoWork():
    max_w = 120 #ширина объекта
    max_h = 200 #высота объекта
    count_detect = 0 # количество кадров, когда объект был в обзоре
    global frame_end
    #поиск подходящей камеры
    #(под Linux может инициализироваться в разных местах)
    for i in range(5):
        print("Camera = /dev/video"+str(i))
        camera = cv2.VideoCapture("/dev/video"+str(i))
        if (camera.isOpened() == True):
            print("webcam open video"+str(i))
            break
        else:
            print("not open /dev/video"+str(i))
    

    kernal = np.ones((5, 5), np.uint8)  # form a 5x5 matrix with all ones range is 8-bit
    motion_threshold = 1500  # decrease this value to increase sensitivity (уменьшите это значение чтобы увеличить чувствительность)
    while True:
        success, frame = camera.read()  # read the camera frame
        success2, frame2 = camera.read()  # read the camera frame
        if (camera.isOpened() == True):
            frame_gray_1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_gray_2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            diffImage = cv2.absdiff(frame_gray_1, frame_gray_2)  # определяем разницу между двумя кадрами
            blurImage = cv2.GaussianBlur(diffImage, (5, 5), 0)
            _, thresholdImage = cv2.threshold(blurImage, 20, 255, cv2.THRESH_BINARY)
            dilatedImage = cv2.dilate(thresholdImage, kernal, iterations=5)
            contours, _ = cv2.findContours(dilatedImage, cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)  # find contour is a magic function
            for contour in contours:  # for every change that is detected
                (x, y, w, h) = cv2.boundingRect(contour)  # находим местоположение где зафиксировано изменение
                if cv2.contourArea(contour) > motion_threshold:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
                    cv2.putText(frame,"w="+str(w)+"h="+str(h),(x+5, y+5), cv2.FONT_HERSHEY_SIMPLEX,1,(255, 0, 0), 1)
                if ((max_w <= w) and (max_h <= h)):
                    count_detect=count_detect + 1
                    if (count_detect == 60):
                        print("!!!WARNING!!! Foreign object!")
                        count_detect=0
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_end = buffer.tobytes()

def gen_frames():
    global frame_end
    while(True):
        #TODO: необходима задержка(видимо нужен блок для переключения потоков)
        time.sleep(0.05)
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_end + b'\r\n')

@app.route('/')
def index():
       return render_template('index_2.html')

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
            wiringpi.delay(800)
            wiringpi.softPwmStop(PIN_TO_PWM_0)
  #          wiringpi.delay(200)
       
        s1 = request.form['green']
        if (pwm_tilt != int(s1)):
            pwm_tilt = int(s1)
            wiringpi.delay(100)
            wiringpi.softPwmWrite(PIN_TO_PWM_1,pwm_tilt)
            wiringpi.delay(800)

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

def runApp():
    #app.run(host="localhost", port=8086, debug=False)
    app.run(host="192.168.0.124", port=8086, debug=False)

if __name__ == "__main__":
    try:
        print(f'start first thread')
        t1 = Thread(target=runApp).start()
        print(f'start second thread')
        t2 = Thread(target=videoWork).start()
    except Exception as e:
        print("Unexpected error:" + str(e))
