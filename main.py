import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://faceattendancerealtime-bcd95-default-rtdb.firebaseio.com/',
    'storageBucket': "faceattendancerealtime-bcd95.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

#Importing mode images

folderModePath = 'Resources/Modes'
modePath = os.listdir(folderModePath)
imgModeList = []
for path in modePath:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

#load the encoding file
file = open("EncodeFile.p", "rb")
encodingListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodingListKnownWithIds

modeType = 0
encounter = 0
id = -1

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgS)
    encodeCurrentFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)
    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurrentFrame:
        for encodeFace, faceloc in zip(encodeCurrentFrame, faceCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            print("facedis", faceDis)

            matchindex = np.argmin(faceDis)
            # print("Match Index", matchindex)
            if min(faceDis) > 0.5:
                matches[matchindex] = False

            if matches[matchindex]:
                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 162+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchindex]
                if encounter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face_Attendance", imgBackground)
                    cv2.waitKey(1)
                    encounter = 1
                    modeType = 1

            if encounter != 0:

                if encounter == 1:
                    #Get the data
                    studentInfo = db.reference(f'Students/{id}').get()
                    print(studentInfo)

                    #Get the image
                    blob = bucket.get_blob(f'Images/{id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                    # update data of attendance
                    dateTimeObject = datetime.strptime(studentInfo['Last_attendance_time'],
                                                      "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now()-dateTimeObject).total_seconds()
                    if secondsElapsed>30:
                        ref = db.reference(f'Students/{id}')
                        studentInfo['Total_attendance'] += 1
                        ref.child("Total_attendance").set(studentInfo['Total_attendance'])
                        ref.child("Last_attendance_time").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType = 3
                        encounter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                if modeType != 3:
                    if 10 < encounter < 20:
                        modeType = 2
                    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]
                    if encounter <= 10:

                        cv2.putText(imgBackground, str(studentInfo['Total_attendance']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['Major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                    (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                    (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['Grade']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                    (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['Year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                    (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['Starting_Year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                    (100, 100, 100), 1)

                        (w, h), _ = cv2.getTextSize(studentInfo['Name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414-w)//2
                        cv2.putText(imgBackground, str(studentInfo['Name']), (808+offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1,
                                    (0, 0, 0), 1)

                        imgBackground[175:175+216, 909:909+216] = imgStudent

                    encounter += 1

                    if encounter >= 20:
                        encounter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        encounter = 0

    cv2.imshow("Face_Attendance", imgBackground)
    cv2.waitKey(1)
