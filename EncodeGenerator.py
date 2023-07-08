import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://faceattendancerealtime-bcd95-default-rtdb.firebaseio.com/',
    'storageBucket': "faceattendancerealtime-bcd95.appspot.com"
})

folderPath = 'Images'
modePath = os.listdir(folderPath)
imgList = []
studentIds = []
for name in modePath:
    studentIds.append(os.path.splitext(name)[0])
print(studentIds)
for path in modePath:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

def findEncodings(imagesList):

    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print("Encoding Started")
encodeListKnown = findEncodings(imgList)
encodingListKnownWithIds = [encodeListKnown, studentIds]
print(encodeListKnown)

file = open("EncodeFile.p", "wb")
pickle.dump(encodingListKnownWithIds, file)
file.close()
print("File Saved")
