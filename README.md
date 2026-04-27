# Face Recognition & Attendance System

## 🚀 Features
- **GUI Interface** with buttons for all functions
- **CSV-based persistence** for user and attendance data
- **Automatic Photo Capture** (50 photos every 0.1 seconds)
- **Face Recognition** with attendance tracking
- **Real-time Recognition** with security features
- **Data Export** to CSV files

## 📋 Prerequisites

### 1. Install Required Python Packages
```bash
pip install opencv-python opencv-contrib-python pandas numpy tkinter Pillow
```

## 🛠️ Setup Instructions

### Step 1: Run setup
```bash
python setup.py
```

### Step 2: Capture faces
```bash
python takephotos.py
```

### Step 3: Train the model
```bash
python train.py
```

### Step 4: Start recognition
```bash
python recognize.py
```

## 🎯 How to Use

### 1. Record New Face
- Run `takephotos.py`
- Enter ID (1-10000) and name
- Position face in camera view
- Photos are captured automatically (50 photos total)

### 2. Train Model
- Run `train.py`
- The model is trained using captured face images

### 3. Start Recognition
- Run `recognize.py`
- Camera opens for live recognition
- Green box = recognized (attendance recorded)
- Red box = unknown

### 4. View Attendance
- Open `attendance.csv` in Excel or a text editor
- Attendance records are stored in CSV format

## 📁 File Structure
```
mini project/
├── takephotos.py        # Photo capture module
├── train.py            # Model training module
├── recognize.py        # Face recognition module
├── setup.py           # Initial setup for files and directories
├── id-names.csv       # User database
├── attendance.csv     # Attendance records
├── haarcascade_frontalface_alt.xml  # Face detection model
├── Classifiers/       # Trained models directory
└── faces/            # Training photos directory
```

## 🔧 Configuration

### System Settings
- **Photos per person:** 50 (modify `total_photos_needed` in takephotos.py)
- **Capture interval:** 0.1 seconds (modify `capture_interval` in takephotos.py)
- **Recognition threshold:** 70 (modify trust threshold in recognize.py)

## 🐛 Troubleshooting

### Camera Issues
1. Check camera permissions
2. Ensure no other applications are using the camera
3. Try different camera index in `cv.VideoCapture(0)`

### Recognition Issues
1. Ensure sufficient training photos (50+ recommended)
2. Train model after adding new faces
3. Check lighting conditions
4. Adjust recognition threshold if needed

## 🎉 Features Overview
- ✅ GUI with intuitive buttons
- ✅ CSV-based persistence
- ✅ Automatic photo capture
- ✅ Real-time face recognition
- ✅ Attendance tracking
- ✅ Data export capabilities
- ✅ Duplicate attendance prevention

Enjoy your Face Recognition System! 🤖📸