#Import necessary libraries
from flask import Flask, render_template, Response
import cv2
import numpy as np
#Initialize the Flask app
app = Flask(__name__)
hsv_min = np.array((159,131,32), np.uint8)
hsv_max = np.array((226, 255, 231), np.uint8)

def gen_frames():
    camera = cv2.VideoCapture(0)
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
    app.run(debug=True)