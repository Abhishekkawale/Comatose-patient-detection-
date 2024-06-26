import cv2
import time
import pandas
from datetime import datetime

import smtplib
import threading
from email.mime.text import MIMEText
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")



gmail_user = "abhishekkawale07@gmail.com"
gmail_pwd = "Abhikawale@07"
first_frame = None
status_list = [None, None]
times = []
etime = []
df = pandas.DataFrame(columns=["Start", "End"])

video = cv2.VideoCapture(0)
start_time = time.time()
flag = 1
mode=int(input("Enter 1 for Motion Detection 2 for Intrusion Detection"))


def mail():
    smtp_ssl_host = 'smtp.gmail.com'  # smtp.mail.yahoo.com
    smtp_ssl_port = 465
    username = 'abhishekkawale07@gmail.com'
    password = 'Abhikawale@07'
    sender = 'abhishekkawale07@gmail.com'
    targets = ['savani.limbekar@gamil.com']

    msg = MIMEText('Intrusion is occuring')
    msg['Subject'] = 'Security Alert'
    msg['From'] = sender
    msg['To'] = ', '.join(targets)

    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(username, password)
    server.sendmail(sender, targets, msg.as_string())
    server.quit()


while True:

    check, frame = video.read()
    status = 0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    if first_frame is None:
            first_frame = gray
            continue
    
    if mode == 1:
        

        delta_frame = cv2.absdiff(first_frame, gray)
        thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

        (_, cnts, _) = cv2.findContours(thresh_frame.copy(),
                                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in cnts:
            if cv2.contourArea(contour) < 10000:
                continue
            status = 1

            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

    else:
        faces=face_cascade.detectMultiScale(gray,scaleFactor=1.05,minNeighbors=5)

        for x,y,w,h in faces:
            frame=cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),3)
            status=1
 
        if first_frame is None:
            first_frame=gray
            continue

        delta_frame=cv2.absdiff(first_frame,gray)
        thresh_frame=cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame=cv2.dilate(thresh_frame, None, iterations=2)

        (_,cnts,_)=cv2.findContours(thresh_frame.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in cnts:
            if cv2.contourArea(contour) < 10000:
                continue
            
    
    
    
    status_list.append(status)

    status_list = status_list[-2:]

    if status_list[-1] == 1 and status_list[-2] == 0:
        times.append(datetime.now())
        start_time = time.time()
        print("Enter")
        cv2.imwrite("yolo.jpg", frame)
        flag = 0

    if status_list[-1] == 0 and status_list[-2] == 1:
        times.append(datetime.now())
        flag = 1
        print("exit")

    elapsed_time = time.time() - start_time

    if elapsed_time > 3 and flag == 0:
        print("intruder")
        if len(etime) == 0:
            etime.append(time.time())
            t1 = threading.Thread(target=mail, args=())
            t1.start()

        else:
            etime.append(time.time())
        emailtimelapse = etime[-1]-time.time()
        if emailtimelapse > 50000:
            mail()
        flag = 1

    cv2.imshow("Gray Frame", gray)
    cv2.imshow("Delta Frame", delta_frame)
    cv2.imshow("Threshold Frame", thresh_frame)
    cv2.imshow("Color Frame", frame)

    key = cv2.waitKey(1)

    if key == ord('q'):
        if status == 1:
            times.append(datetime.now())
        break

print(status_list)
print(times)


for i in range(0, len(times), 2):
    df = df.append({"Start": times[i], "End": times[i+1]}, ignore_index=True)

df.to_csv("Times.csv")

video.release()
cv2.destroyAllWindows
