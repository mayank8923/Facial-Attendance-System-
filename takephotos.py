import os
import numpy as np
import pandas as pd
import cv2 as cv
from datetime import datetime
import time

id_names_file = 'id-names.csv'
faces_dir = 'faces'

if os.path.exists(id_names_file):
    id_names = pd.read_csv(id_names_file)
    if 'id' not in id_names.columns or 'name' not in id_names.columns:
        id_names = pd.DataFrame(columns=['id', 'name'])
else:
    id_names = pd.DataFrame(columns=['id', 'name'])
    id_names.to_csv(id_names_file, index=False)

os.makedirs(faces_dir, exist_ok=True)

print('Welcome!')
print('\nPlease put in your ID.')
print('If this is your first time choose a random ID between 1-10000')

while True:
    try:
        user_id = int(input('ID: '))
        break
    except ValueError:
        print('Please enter a valid numeric ID.')

name = ''

if user_id in id_names['id'].values:
    name = id_names[id_names['id'] == user_id]['name'].item()
    print(f'Welcome Back {name}!!')
else:
    name = input('Please enter your name: ').strip()
    os.makedirs(os.path.join(faces_dir, str(user_id)), exist_ok=True)
    id_names = pd.concat([id_names, pd.DataFrame({'id': [user_id], 'name': [name]})], ignore_index=True)
    id_names.to_csv(id_names_file, index=False)

print("\nLet's capture!")
print("Photos will be captured automatically every 0.1 seconds.")
print("Position your face in different angles and poses for better recognition.")
print("Total photos to capture: 50")
input("\nPress ENTER to start, and press 'q' to quit early!")

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

camera.release()
cv.destroyAllWindows()

if photos_taken >= total_photos_needed:
    print(f"\n✓ Capture complete! {photos_taken} photos taken successfully!")
else:
    print(f"\nCapture stopped. {photos_taken} photos taken.")