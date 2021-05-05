import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import mongoRead
# from PIL import ImageGrab

path = 'ImagesAttendance'
images = []
classNames = []
classNamesDict = dict()
myList = []
for c in os.listdir(path):
    if(c != ".DS_Store"):
        myList.append(c)
print(myList)
for cl in myList:
    imgFile = []
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    imgFile = os.path.splitext(cl)[0].split("_")
    classNames.append(imgFile[0])
    classNamesDict[(imgFile[0])] = imgFile[1]
print(classNamesDict)


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendance(name):
    now = datetime.now()
    dtString = now.strftime('%H:%M:%S')
    dateStr = now.strftime('%d-%m-%y')
    mongoRead.insert(name=name,
                     number=int(("1910102"+classNamesDict[name])),
                     date=dateStr,
                     time=dtString
                     )


encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    #img = captureScreen()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].lower()
            # print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1+6, y2-6),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            markAttendance(name)

    cv2.imshow('Webcam', img)
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
cap.release()
cv2.destroyAllWindows()
