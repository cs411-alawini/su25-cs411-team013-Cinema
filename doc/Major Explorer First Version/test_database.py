#!/usr/bin/env python3
"""
Database connection and table creation test script
Run this to check if your database setup is working correctly
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    """Test database connection and table creation"""
    
    # Database configuration
    config = {
        'user': os.getenv('DB_USER', 'apalu3'),
        'password': os.getenv('DB_PASSWORD', 'password328'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'college_major_db'),
        'port': int(os.getenv('DB_PORT', '3306'))
    }
    
    print("Testing database connection...")
    print(f"Host: {config['host']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    print(f"Port: {config['port']}")
    print("-" * 50)
    
    try:
        # Test connection
        conn = mysql.connector.connect(**config)
        print("✅ Database connection successful!")
        
        cursor = conn.cursor()
        
        # Check if User table exists
        cursor.execute("SHOW TABLES LIKE 'User'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ User table exists!")
            
            # Check table structure
            cursor.execute("DESCRIBE User")
            columns = cursor.fetchall()
            print("\nUser table structure:")
            for col in columns:
                print(f"  {col[0]} - {col[1]}")
            
            # Check if table is empty
            cursor.execute("SELECT COUNT(*) FROM User")
            count = cursor.fetchone()[0]
            print(f"\nNumber of users in table: {count}")
            
        else:
            print("❌ User table does not exist!")
            print("\nCreating User table...")
            
            # Create the User table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS User (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
            """
            
            cursor.execute(create_table_sql)
            
            # Create indexes
            cursor.execute("CREATE INDEX idx_user_username ON User(username)")
            cursor.execute("CREATE INDEX idx_user_email ON User(email)")
            
            conn.commit()
            print("✅ Users table created successfully!")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e.msg} (Error code: {e.errno})")
        
        if e.errno == 1045:  # Access denied
            print("This usually means incorrect username/password")
        elif e.errno == 1049:  # Unknown database
            print("The database 'college_major_db' does not exist. Please create it first.")
        elif e.errno == 2003:  # Can't connect to server
            print("Cannot connect to MySQL server. Make sure it's running.")
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_database_connection() 