import os
import numpy as np
import cv2 as cv
from database import DatabaseManager, create_database_if_not_exists

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''  # Change to your MySQL password if set
DB_NAME = 'facial_attendance'

faces_dir = 'faces'
model_dir = 'Classifiers'
model_file = os.path.join(model_dir, 'TrainedLBPH.yml')

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

# Validate face directory
if not os.path.exists(faces_dir):
    raise FileNotFoundError(f"Faces directory not found: {faces_dir}")

# Check for OpenCV face module
if not hasattr(cv, 'face') or not hasattr(cv.face, 'LBPHFaceRecognizer_create'):
    raise ImportError('OpenCV face module is not available. Install opencv-contrib-python.')

# Create LBPH recognizer
lbph = cv.face.LBPHFaceRecognizer_create(threshold=50)


def create_train():
    """Load and prepare training data from faces directory"""
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
            except Exception as e:
                print(f"⚠ Error loading {img_path}: {e}")
    return faces, labels


try:
    # Load training data
    print("Loading training data...")
    faces, labels = create_train()

    if len(faces) == 0:
        raise RuntimeError('No training images found in the faces directory.')

    print(f"✓ Loaded {len(faces)} training images")
    
    # Get unique user IDs from training data
    unique_labels = set(labels)
    print(f"✓ Found {len(unique_labels)} users with training data")
    
    # Verify all users are in database
    print("\nSyncing users with database...")
    for user_id in unique_labels:
        if not db.get_user(user_id):
            print(f"⚠ Warning: User ID {user_id} has training data but not registered in database")
            # Optionally add placeholder user
            db.add_user(user_id, f"User_{user_id}")
    
    # Train the model
    print("\n🔄 Training Started...")
    faces_array = np.array(faces)
    labels_array = np.array(labels)
    lbph.train(faces_array, labels_array)
    
    # Save model
    if not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)
    lbph.save(model_file)
    
    print('✓ Training Complete!')
    print(f"✓ Model saved to: {model_file}")
    print(f"✓ Ready for face recognition with {len(unique_labels)} users")

except Exception as e:
    print(f"✗ Error during training: {e}")
    exit(1)

finally:
    db.disconnect()
