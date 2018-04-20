import cv2
import matplotlib.pyplot as plt
import math
from pyzbar.pyzbar import decode

cap = cv2.VideoCapture(0)

class res:
    def __init__(self):
        self.a = 0
        self.b = 0
        self.center = []
        self.status = False
    def __str__(self):
        return ('a=%d b=%d center=%s status=%s' % ((self.a), (self.b), (self.center),(self.status)))

def distance(centers, width, height, img_qr):
    top_left, bot_left, right = [], [], []
    # print("centers: ", centers)
    # print("lim_x: %d  , lim_y: %d" %((width / 2), (height / 2)))
    for c in centers:
        chk = True
        # print(c[0])
        if (c[0] < (width / 2)):  # Left
            if (c[1] < (height / 2)):  # Top-left
                top_left = c
            else:
                bot_left = c
        else:
            right = c
    if (top_left != [] and bot_left != [] and right != []):
        cv2.line(img_qr, (top_left[0], top_left[1]), (right[0], right[1]), (255, 0, 0), 3)
        cv2.line(img_qr, (top_left[0], top_left[1]), (bot_left[0], bot_left[1]), (0, 255, 0), 3)
        a = math.sqrt(pow((top_left[0]-right[0]),2)+pow((top_left[1]-right[1]),2))
        b = math.sqrt(pow((top_left[0]-bot_left[0]),2)+pow((top_left[1]-bot_left[1]),2))
        cv2.imshow("center_iine", img_qr)
    else:
        a, b = 0, 0
    return a, b

def center(obj, img_qr):
    centers =[]
    if (len(obj) != 0):
        for i in range(len(obj)):
          moments = cv2.moments(obj[i])
          centers.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
          cv2.circle(img_qr, centers[-1], 1, (255, 100, 0), -1)
        # cv2.imshow("center", img_qr)
        # print(centers)
    return centers

def contour(frame, x1, y1, x2, y2):
    obj = []
    a, b = 0, 0
    margin = 5
    height, width = (y2-y1), (x2-x1)

    crop_img = frame[y1-margin:y2+margin, x1-margin:x2+margin]
    img_qr = crop_img

    img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY, dstCn=0)

    # img = cv2.GaussianBlur(img, (5, 5), 0)
    # cv2.imshow("gauss", img)

    ret, thresh = cv2.threshold(img, 100, 255, 0)
    cv2.imshow("thres", thresh)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(img_qr, contours, -1, (255, 0, 255), 2)
    # cv2.imshow("im", img_qr)
    # print(hierarchy[0])
    # print("_____________________")
    hrc = hierarchy[0]
    for i in range(0, len(hrc)):
        # next = hrc[i][0]
        previous = hrc[i][1]
        first_child = hrc[i][2]
        parent = hrc[i][3]
        if ((previous != -1) and (first_child != -1) and (parent == 0)):
            for j in range(0, len(hrc)):
                pair_parent = hrc[j][3]
                if (first_child == pair_parent):
                    # print(hrc[i])
                    cv2.drawContours(img_qr, [contours[i]], -1, (255, 0, 255), 2)
                    # cv2.imshow("im", img_qr)
                    obj.append(contours[i])
    # print("contour: ", obj)
    centers = center(obj, img_qr)
    if (centers != []):
        a, b = distance(centers, width, height, img_qr)
    else:
        print("centers == []")
    return a, b

if __name__ =="__main__":
    fig = plt.figure()
    while(1):
        ret, frame = cap.read()
        if(ret):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow('gray', gray)
            result = decode(gray)
            # print(result)
            a, b = 0, 0
            response = res()

            if (result != []):
                for p in [result]:
                    # print ('%d, %d, %d, %d' %(p[0][2][0], p[0][2][1],  p[0][2][2], p[0][2][3]))  ##access to rect
                    x1, y1 = (p[0][2][0]), (p[0][2][1])
                    x2, y2 = (p[0][2][0]+p[0][2][2]), (p[0][2][1]+p[0][2][3])

                    # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    response.center = (round((x1 + x2) / 2), round((y1 + y2) / 2))
                    cv2.circle(frame, response.center, 1, (0, 255, 255), 3)
                    # cv2.imshow('draw', frame)
                    response.a, response.b = contour(frame, x1, y1, x2, y2)
                    if (response.a==0 or response.b == 0 or response.center == []):
                        response.status = False
                    else:
                        response.status = True
                    print("res: ", str(response))
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()