import mysql.connector
from mysql.connector import Error
import os

class DatabaseManager:
    """Manages MySQL database connections and operations"""
    
    def __init__(self, host='localhost', user='root', password='', database='facial_attendance'):
        """
        Initialize database manager
        
        Args:
            host: MySQL server host
            user: MySQL username
            password: MySQL password
            database: Database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print(f"✓ Connected to MySQL database: {self.database}")
            return True
        except Error as e:
            print(f"✗ Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Disconnected from MySQL database")
    
    def create_tables(self):
        """Create required tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Create users table
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
            """
            
            # Create attendance table
            create_attendance_table = """
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE KEY unique_attendance (user_id, date)
            );
            """
            
            cursor.execute(create_users_table)
            cursor.execute(create_attendance_table)
            self.connection.commit()
            print("✓ Database tables created successfully")
            cursor.close()
            return True
        except Error as e:
            print(f"✗ Error creating tables: {e}")
            return False
    
    def add_user(self, user_id, name):
        """Add or update user in database"""
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO users (id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name = %s"
            cursor.execute(query, (user_id, name, name))
            self.connection.commit()
            cursor.close()
            print(f"✓ User added/updated: ID={user_id}, Name={name}")
            return True
        except Error as e:
            print(f"✗ Error adding user: {e}")
            return False
    
    def record_attendance(self, user_id, name, date, time):
        """Record attendance in database"""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO attendance (user_id, name, date, time) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            time = %s, recorded_at = CURRENT_TIMESTAMP
            """
            cursor.execute(query, (user_id, name, date, time, time))
            self.connection.commit()
            cursor.close()
            print(f"✓ Attendance recorded: {name} at {time}")
            return True
        except Error as e:
            print(f"✗ Error recording attendance: {e}")
            return False
    
    def get_user(self, user_id):
        """Get user information"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"✗ Error fetching user: {e}")
            return None
    
    def get_all_users(self):
        """Get all users from database"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM users ORDER BY id"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"✗ Error fetching users: {e}")
            return []
    
    def get_attendance(self, user_id=None, date=None):
        """Get attendance records with optional filters"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM attendance WHERE 1=1"
            params = []
            
            if user_id is not None:
                query += " AND user_id = %s"
                params.append(user_id)
            if date is not None:
                query += " AND date = %s"
                params.append(date)
            
            query += " ORDER BY recorded_at DESC"
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"✗ Error fetching attendance: {e}")
            return []
    
    def check_attendance_today(self, user_id, date):
        """Check if user has attended today"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM attendance WHERE user_id = %s AND date = %s"
            cursor.execute(query, (user_id, date))
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Error as e:
            print(f"✗ Error checking attendance: {e}")
            return False


def create_database_if_not_exists(host='localhost', user='root', password=''):
    """Create database if it doesn't exist"""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS facial_attendance")
        connection.commit()
        cursor.close()
        connection.close()
        print("✓ Database 'facial_attendance' ready")
        return True
    except Error as e:
        print(f"✗ Error creating database: {e}")
        return False
