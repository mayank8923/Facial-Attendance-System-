import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Change this to your MySQL username
            password='YOUR_PASSWORD'  # Change this to your MySQL password
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS face_recognition_db")
            print("Database 'face_recognition_db' created successfully")

            # Switch to the database
            cursor.execute("USE face_recognition_db")

            # Create users table
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_users_table)
            print("Users table created successfully")

            # Create attendance table
            create_attendance_table = """
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                name VARCHAR(100),
                date DATE,
                time TIME,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
            cursor.execute(create_attendance_table)
            print("Attendance table created successfully")

            print("Database setup complete!")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    create_database()
