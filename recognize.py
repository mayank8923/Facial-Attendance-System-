import os
import cv2 as cv
from datetime import datetime
from database import DatabaseManager, create_database_if_not_exists

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''  # Change to your MySQL password if set
DB_NAME = 'facial_attendance'

face_model_file = 'Classifiers/TrainedLBPH.yml'
face_cascade_file = 'haarcascade_frontalface_alt.xml'

# Initialize and setup database
print("Initializing database...")
if not create_database_if_not_exists(DB_HOST, DB_USER, DB_PASSWORD):
    print("✗ Failed to create database. Please check your MySQL installation.")
    exit(1)

db = DatabaseManager(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
if not db.connect():
    print("✗ Failed to connect to database. Please check your MySQL credentials.")
    exit(1)

if not db.create_tables():
    print("✗ Failed to create tables. Please check your database permissions.")
    db.disconnect()
    exit(1)

# Validate required files
if not os.path.exists(face_cascade_file):
    raise FileNotFoundError(f"Required file not found: {face_cascade_file}")

if not os.path.exists(face_model_file):
    raise FileNotFoundError(f"Face recognition model not found: {face_model_file}")

# Load face cascade classifier
faceClassifier = cv.CascadeClassifier(face_cascade_file)
if faceClassifier.empty():
    raise ValueError(f"Failed to load cascade classifier from {face_cascade_file}")

# Check for OpenCV face module
if not hasattr(cv, 'face') or not hasattr(cv.face, 'LBPHFaceRecognizer_create'):
    raise ImportError("OpenCV face module is not available. Install opencv-contrib-python.")

# Load trained LBPH model
lbph = cv.face.LBPHFaceRecognizer_create(threshold=50)
lbph.read(face_model_file)

# Initialize camera
camera = cv.VideoCapture(0)
if not camera.isOpened():
    raise SystemError("Could not open camera. Check that a camera is connected and accessible.")

recognized_today = {}
print("Starting face recognition. Press 'q' in the window to quit.")
print("\nCamera Status:")
print("  🟢 Green box = Recognized (attendance recorded)")
print("  🟡 Orange box = Unknown ID")
print("  🔴 Red box = Unknown face\n")

try:
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
                # Get user from database
                user = db.get_user(label)
                if user:
                    name = user['name']
                    cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv.putText(img, name, (x, y + h + 30), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

                    today = datetime.now().strftime('%Y-%m-%d')
                    key = (label, today)

                    # Record attendance if not already recorded today
                    if key not in recognized_today:
                        current_time = datetime.now().strftime('%H:%M:%S')
                        if db.record_attendance(label, name, today, current_time):
                            recognized_today[key] = True
                            print(f"✓ Attendance recorded for {name} at {current_time}")
                else:
                    # Unknown ID in database
                    cv.rectangle(img, (x, y), (x + w, y + h), (0, 165, 255), 2)
                    cv.putText(img, 'Unknown ID', (x, y + h + 30), cv.FONT_HERSHEY_COMPLEX, 0.8, (0, 165, 255), 2)
            else:
                # Unknown face
                cv.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv.putText(img, 'Unknown', (x, y + h + 30), cv.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

        cv.imshow('Recognize', img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    camera.release()
    cv.destroyAllWindows()
    db.disconnect()
    print("\n✓ Attendance recording completed!")
    print("✓ Data saved to MySQL database")
