import os
import pandas as pd
import numpy as np
import cv2 as cv

id_names_file = 'id-names.csv'
faces_dir = 'faces'
model_dir = 'Classifiers'
model_file = os.path.join(model_dir, 'TrainedLBPH.yml')

if not os.path.exists(id_names_file):
    pd.DataFrame(columns=['id', 'name']).to_csv(id_names_file, index=False)

if not os.path.exists(faces_dir):
    raise FileNotFoundError(f"Faces directory not found: {faces_dir}")

if not hasattr(cv, 'face') or not hasattr(cv.face, 'LBPHFaceRecognizer_create'):
    raise ImportError('OpenCV face module is not available. Install opencv-contrib-python.')

lbph = cv.face.LBPHFaceRecognizer_create(threshold=50)


def create_train():
    faces = []
    labels = []
    for person_id in os.listdir(faces_dir):
        path = os.path.join(faces_dir, person_id)
        if not os.path.isdir(path):
            continue
        for img_name in os.listdir(path):
            img_path = os.path.join(path, img_name)
            try:
                face = cv.imread(img_path)
                if face is None:
                    continue
                face = cv.cvtColor(face, cv.COLOR_BGR2GRAY)
                faces.append(face)
                labels.append(int(person_id))
            except Exception:
                pass
    return faces, labels


faces, labels = create_train()

if len(faces) == 0:
    raise RuntimeError('No training images found in the faces directory.')

print('Training Started')
faces_array = np.array(faces)
labels_array = np.array(labels)
lbph.train(faces_array, labels_array)
if not os.path.exists(model_dir):
    os.makedirs(model_dir, exist_ok=True)
lbph.save(model_file)
print('Training Complete!')