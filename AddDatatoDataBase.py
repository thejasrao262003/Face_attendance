import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://faceattendancerealtime-bcd95-default-rtdb.firebaseio.com/'
})

ref = db.reference('Students')

data = {
    '321654':
        {
            'Name': "Thejas P Rao",
            "Major": "CSE",
            "Starting_Year": 2021,
            "Total_attendance": 6,
            "Grade": "S",
            'Year': 3,
            "Last_attendance_time": "2023-07-06 00:54:34"
        },
    '852741':
        {
            'Name': "Emily Blunt",
            "Major": "MBA",
            "Starting_Year": 2022,
            "Total_attendance": 3,
            "Grade": "A",
            'Year': 1,
            "Last_attendance_time": "2023-07-06 00:12:34"
        },
    '963852':
        {
            'Name': "Elon Musk",
            "Major": "BCA",
            "Starting_Year": 2022,
            "Total_attendance": 5,
            "Grade": "A",
            'Year': 2,
            "Last_attendance_time": "2023-07-06 00:44:34"
        }
}

for key, value in data.items():
    ref.child(key).set(value)