import cv2
import numpy as np
import video

if __name__ == '__main__':
    def callback(*arg):
        print (arg)

def createPath( img ):
    h, w = img.shape[:2]
    return np.zeros((h, w, 3), np.uint8)

cv2.namedWindow( "result" )

cap = video.create_capture(0)
hsv_min = np.array((0,168, 142), np.uint8)
hsv_max = np.array((190, 255, 255), np.uint8)

lastx = 0
lasty = 0
path_color = (0,0,255)

flag, img = cap.read()
path = createPath(img)

while True:
    flag, img = cap.read()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV )
    thresh = cv2.inRange(hsv, hsv_min, hsv_max)

    moments = cv2.moments(thresh, 1)
    dM01 = moments['m01']
    dM10 = moments['m10']
    dArea = moments['m00']

    if dArea > 3000:
        x = int(dM10 / dArea)
        y = int(dM01 / dArea)
        cv2.circle(img, (x, y), 10, (0,0,255), -1)

    if lastx > 0 and lasty > 0:
        cv2.line(path, (lastx, lasty), (x,y), path_color, 5)
    lastx = x
    lasty = y

    # накладываем линию траектории поверх изображения
    img = cv2.add( img, path)

    cv2.imshow('result', img)

    ch = cv2.waitKey(5)
    if ch == 27:
        break

cap.release()
cv2.destroyAllWindows()
