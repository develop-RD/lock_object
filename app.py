#!/usr/bin/env python
from datetime import datetime
from flask import Flask, render_template, Response
import numpy as np
import cv2
#Initialize the Flask app
app = Flask(__name__)
#camera = cv2.VideoCapture("/dev/video2")

#if not camera.isOpened():
#    print("cannot open camera, but why?")
#else:
#    print("Open camera")

'''
for ip camera use - rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' 
for local webcam use cv2.VideoCapture(0)
'''

#cap = cv2.VideoCapture("/dev/video2")

# HSV фильтр для зеленых объектов из прошлого урока
#hsv_min = np.array((12,61, 128), np.uint8)
#hsv_max = np.array((57, 203, 216), np.uint8)
hsv_min = np.array((17,13, 90), np.uint8)
hsv_max = np.array((114, 28, 209), np.uint8)



def gen_frames():
    camera = cv2.VideoCapture("/dev/video0")
    while True:
        success, frame = camera.read()  # read the camera frame
        if success:
            #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # преобразуем RGB картинку в HSV модель
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # применяем цветовой фильтр
            thresh = cv2.inRange(hsv, hsv_min, hsv_max)

            # вычисляем моменты изображения
            moments = cv2.moments(thresh, 1)
            dM01 = moments['m01']
            dM10 = moments['m10']
            dArea = moments['m00']
            # будем реагировать только на те моменты,
            # которые содержать больше 100 пикселей
            if dArea > 3000:
                x = int(dM10 / dArea)
                y = int(dM01 / dArea)
                cv2.circle(frame, (x, y), 10, (0, 0, 255), -1)
            ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            print("dont open camera")
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="192.168.0.104",port=8080,debug=True)
