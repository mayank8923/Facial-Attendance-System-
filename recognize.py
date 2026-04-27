import os
import pandas as pd
import cv2 as cv
from datetime import datetime

attendance_file = 'attendance.csv'
id_names_file = 'id-names.csv'
face_model_file = 'Classifiers/TrainedLBPH.yml'
face_cascade_file = 'haarcascade_frontalface_alt.xml'

# Ensure required files and directories exist
if not os.path.exists(id_names_file):
    pd.DataFrame(columns=['id', 'name']).to_csv(id_names_file, index=False)

if not os.path.exists(face_cascade_file):
    raise FileNotFoundError(f"Required file not found: {face_cascade_file}")

if not os.path.exists(attendance_file):
    pd.DataFrame(columns=['ID', 'Name', 'Date', 'Time']).to_csv(attendance_file, index=False)

id_names = pd.read_csv(id_names_file)
if 'id' not in id_names.columns or 'name' not in id_names.columns:
    id_names = pd.DataFrame(columns=['id', 'name'])
else:
    id_names = id_names[['id', 'name']]

faceClassifier = cv.CascadeClassifier(face_cascade_file)
if faceClassifier.empty():
    raise ValueError(f"Failed to load cascade classifier from {face_cascade_file}")

if not hasattr(cv, 'face') or not hasattr(cv.face, 'LBPHFaceRecognizer_create'):
    raise ImportError("OpenCV face module is not available. Install opencv-contrib-python.")

lbph = cv.face.LBPHFaceRecognizer_create(threshold=50)
if os.path.exists(face_model_file):
    lbph.read(face_model_file)
else:
    raise FileNotFoundError(f"Face recognition model not found: {face_model_file}")

camera = cv.VideoCapture(0)
if not camera.isOpened():
    raise SystemError("Could not open camera. Check that a camera is connected and accessible.")

recognized_today = {}
print("Starting face recognition. Press 'q' in the window to quit.")

while True:
    ret, img = camera.read()
    if not ret or img is None:
        print("Failed to read frame from camera. Retrying...")
        continue

    grey = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    faces = faceClassifier.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=4)

    for (x, y, w, h) in faces:
        faceRegion = grey[y:y + h, x:x + w]
        faceRegion = cv.resize(faceRegion, (220, 220))

        label, confidence = lbph.predict(faceRegion)

        if confidence < 70:
            matched = id_names[id_names['id'] == label]
            if not matched.empty:
                name = matched['name'].iloc[0]
                cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv.putText(img, name, (x, y + h + 30), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

                today = datetime.now().strftime('%Y-%m-%d')
                key = (label, today)

                if key not in recognized_today:
                    current_time = datetime.now().strftime('%H:%M:%S')
                    new_record = pd.DataFrame({'ID': [label], 'Name': [name], 'Date': [today], 'Time': [current_time]})
                    attendance_df = pd.read_csv(attendance_file)
                    attendance_df = pd.concat([attendance_df, new_record], ignore_index=True)
                    attendance_df.to_csv(attendance_file, index=False)

                    recognized_today[key] = True
                    print(f"✓ Attendance recorded for {name} at {current_time}")
            else:
                cv.rectangle(img, (x, y), (x + w, y + h), (0, 165, 255), 2)
                cv.putText(img, 'Unknown ID', (x, y + h + 30), cv.FONT_HERSHEY_COMPLEX, 0.8, (0, 165, 255), 2)

        else:
            cv.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv.putText(img, 'Unknown', (x, y + h + 30), cv.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

    cv.imshow('Recognize', img)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv.destroyAllWindows()
print("\nAttendance recording completed!")
print("Check 'attendance.csv' for records")