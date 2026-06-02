import os
import numpy as np
import cv2 as cv
from datetime import datetime
import time
from database import DatabaseManager, create_database_if_not_exists

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''  # Change to your MySQL password if set
DB_NAME = 'facial_attendance'

faces_dir = 'faces'

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

os.makedirs(faces_dir, exist_ok=True)

print('Welcome!')
print('\nPlease put in your ID.')
print('If this is your first time choose a random ID between 1-10000')

# Get user ID
while True:
    try:
        user_id = int(input('ID: '))
        break
    except ValueError:
        print('Please enter a valid numeric ID.')

name = ''

# Check if user already exists in database
existing_user = db.get_user(user_id)
if existing_user:
    name = existing_user['name']
    print(f'Welcome Back {name}!!')
else:
    # New user
    name = input('Please enter your name: ').strip()
    if not name:
        print("✗ Name cannot be empty!")
        db.disconnect()
        exit(1)
    
    # Add user to database
    if db.add_user(user_id, name):
        os.makedirs(os.path.join(faces_dir, str(user_id)), exist_ok=True)
        print(f"✓ User registered: {name} (ID: {user_id})")
    else:
        print("✗ Failed to register user. Please try again.")
        db.disconnect()
        exit(1)

print("\nLet's capture!")
print("Photos will be captured automatically every 0.1 seconds.")
print("Position your face in different angles and poses for better recognition.")
print("Total photos to capture: 50")
input("\nPress ENTER to start, and press 'q' to quit early!")

# Initialize camera
camera = cv.VideoCapture(0)
if not camera.isOpened():
    raise SystemError('Could not open camera. Check that a camera is connected and accessible.')

face_classifier = cv.CascadeClassifier('haarcascade_frontalface_alt.xml')
if face_classifier.empty():
    raise FileNotFoundError('Failed to load face cascade classifier.')

photos_taken = 0
total_photos_needed = 50
last_capture_time = 0
capture_interval = 0.1

try:
    while photos_taken < total_photos_needed:
        ret, img = camera.read()
        if not ret or img is None:
            print('Failed to read camera frame. Retrying...')
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        grey = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
        current_time = time.time()

        for (x, y, w, h) in faces:
            cv.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            face_region = grey[y:y + h, x:x + w]

            if (current_time - last_capture_time) > capture_interval and np.average(face_region) > 50:
                face_img = cv.resize(face_region, (220, 220))
                img_name = f'face.{user_id}.{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.jpg'
                cv.imwrite(os.path.join(faces_dir, str(user_id), img_name), face_img)
                photos_taken += 1
                last_capture_time = current_time
                print(f'{photos_taken}/{total_photos_needed} -> Photos taken!')

        progress_text = f'Photos: {photos_taken}/{total_photos_needed}'
        cv.putText(img, progress_text, (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv.imshow('Face', img)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    camera.release()
    cv.destroyAllWindows()
    db.disconnect()

    if photos_taken >= total_photos_needed:
        print(f"\n✓ Capture complete! {photos_taken} photos taken successfully!")
        print(f"✓ User '{name}' photos saved to database system!")
    else:
        print(f"\n⚠ Capture stopped. {photos_taken} photos taken.")
        print("Please run this script again to capture more photos.")
