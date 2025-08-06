from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
import os
from dotenv import load_dotenv
import bcrypt
import re
from datetime import datetime

load_dotenv() 

app = Flask(__name__)
CORS(app)

config = {
    'user': os.getenv('DB_USER', 'apalu3'),
    'password': os.getenv('DB_PASSWORD', 'password328'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'college_major_db'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

# Helper function to validate email format
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Helper function to validate password strength
def is_valid_password(password):
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 digit
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"

def get_db_connection():
    return mysql.connector.connect(**config)

@app.route('/')
def index():
    return jsonify({"message": "College Major Explorer backend is running!"})

@app.route('/health', methods=['GET'])
def health_check():
    """Check database connection and table existence"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if User table exists
        cursor.execute("SHOW TABLES LIKE 'User'")
        users_table_exists = cursor.fetchone() is not None
        
        # Check if we can query the User table
        users_count = 0
        if users_table_exists:
            cursor.execute("SELECT COUNT(*) FROM User")
            users_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database_connected": True,
            "users_table_exists": users_table_exists,
            "users_count": users_count
        })
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database_connected": False,
            "error": str(e)
        }), 500

# Sign up endpoint using stored procedure
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    # Validation
    if not all([username, email, password, confirm_password]):
        return jsonify({"error": "All fields are required"}), 400
    
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    
    is_valid, password_error = is_valid_password(password)
    if not is_valid:
        return jsonify({"error": password_error}), 400
    
    # Hash password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Call the stored procedure
        cursor.callproc('sp_basic_signup', (username, email, hashed_password.decode('utf-8')))
        
        # Get the user_id from the last insert
        cursor.execute("SELECT LAST_INSERT_ID() as user_id")
        result = cursor.fetchone()
        user_id = result[0] if result else None
        
        conn.commit()
        
        print(f"[SIGNUP_LOG] User {username} (ID: {user_id}) successfully registered with hot majors")
        
        return jsonify({
            "message": "Account created successfully! Welcome to College Major Explorer.",
            "user_id": user_id,
            "username": username
        }), 201
        
    except mysql.connector.Error as e:
        conn.rollback()
        
        # Check if it's the duplicate username/email error from stored procedure
        if e.errno == 1644 and "Username or e-mail already taken" in str(e):
            print(f"[SIGNUP_LOG] Duplicate signup attempt for username: {username}, email: {email}")
            return jsonify({"error": "Username or email already taken"}), 400
        else:
            error_msg = f"MySQL error: {e.msg} (Error code: {e.errno})"
            print(f"[ERROR_LOG] Database error during signup: {error_msg}")
            return jsonify({"error": error_msg}), 500
            
    except Exception as e:
        conn.rollback()
        error_msg = f"Unexpected error: {str(e)}"
        print(f"[ERROR_LOG] Unexpected error during signup: {error_msg}")
        return jsonify({"error": error_msg}), 500
    finally:
        cursor.close()
        conn.close()

# Login endpoint (improved)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username_or_email = data.get('username_or_email')
    password = data.get('password')
    
    if not username_or_email or not password:
        return jsonify({"error": "Username/email and password are required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if input is email or username
        if '@' in username_or_email:
            cursor.execute("SELECT user_id, username, password_hash FROM User WHERE email = %s", (username_or_email,))
        else:
            cursor.execute("SELECT user_id, username, password_hash FROM User WHERE username = %s", (username_or_email,))
        
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "Invalid username/email or password"}), 401
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({
                "message": "Login successful",
                "user_id": user['user_id'],
                "username": user['username']
            })
        else:
            return jsonify({"error": "Invalid username/email or password"}), 401
            
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# Get user profile
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT user_id, username, email FROM User WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify(user)
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/majors', methods=['GET'])
def get_majors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
          m.major_id,
          m.major_name,
          m.interest_area_id,
          ms.avg_salary      AS average_salary,
          ms.job_growth_rate AS job_growth_rate,
          ms.grad_count      AS grads
        FROM MajorStats ms
        JOIN Major m ON m.major_id = ms.major_id
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

@app.route('/interest-areas', methods=['GET'])
def get_interest_areas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT interest_area_id, name FROM InterestArea")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

@app.route('/search-interest-areas', methods=['GET'])
def search_interest_areas():
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Search for interest areas containing the query (case-insensitive)
        cursor.execute(
            "SELECT interest_area_id, name FROM InterestArea WHERE LOWER(name) LIKE LOWER(%s) ORDER BY name",
            (f'%{query}%',)
        )
        results = cursor.fetchall()
        
        return jsonify(results)
        
    except Exception as e:
        print(f"[ERROR_LOG] Error searching interest areas: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/save-comparison', methods=['POST'])
def save_comparison():
    data = request.json
    user_id = data.get('user_id')
    major_ids = data.get('major_ids', [])
    
    if not user_id or not major_ids:
        return jsonify({"error": "Missing user_id or major_ids"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        saved_count = 0
        skipped_count = 0
        trigger_errors = []
        
        for major_id in major_ids:
            try:
                # Try to insert directly - let the MySQL trigger handle duplicates
                cursor.execute(
                    "INSERT INTO SavedComparison (user_id, major_id, saved_at) VALUES (%s, %s, NOW())",
                    (user_id, major_id)
                )
                saved_count += 1
                print(f"[SAVE_LOG] User {user_id} successfully saved major {major_id}")
                
            except mysql.connector.Error as e:
                # Check if this is the duplicate trigger error
                if e.errno == 1644 and "Comparison already saved" in str(e):
                    skipped_count += 1
                    trigger_errors.append(major_id)
                    print(f"[TRIGGER_LOG] User {user_id} attempted duplicate save for major {major_id} - MySQL trigger prevented insertion")
                else:
                    # Re-raise other MySQL errors
                    raise e
        
        conn.commit()
        
        # Log summary
        if saved_count > 0 or skipped_count > 0:
            print(f"[SUMMARY_LOG] User {user_id} save operation: {saved_count} saved, {skipped_count} duplicates prevented")
        
        if saved_count > 0 and skipped_count > 0:
            message = f"Saved {saved_count} new comparisons. {skipped_count} were already saved."
        elif saved_count > 0:
            message = f"Successfully saved {saved_count} comparison(s)."
        else:
            message = f"All {skipped_count} comparison(s) were already saved."
            
        return jsonify({"message": message, "saved": saved_count, "skipped": skipped_count})
        
    except mysql.connector.Error as e:
        conn.rollback()
        error_msg = f"MySQL error: {e.msg} (Error code: {e.errno})"
        print(f"[ERROR_LOG] Database error during save_comparison: {error_msg}")
        return jsonify({"error": error_msg}), 500
    except Exception as e:
        conn.rollback()
        error_msg = f"Unexpected error: {str(e)}"
        print(f"[ERROR_LOG] Unexpected error during save_comparison: {error_msg}")
        return jsonify({"error": error_msg}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/saved-comparisons/<int:user_id>', methods=['GET'])
def get_saved_comparisons(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get saved comparisons grouped by major with average salary
        cursor.execute("""
            SELECT 
                sc.major_id,
                m.major_name,
                AVG(ms.avg_salary) as avg_salary,
                COUNT(ms.stat_id) as job_count,
                sc.saved_at
            FROM SavedComparison sc
            JOIN Major m ON sc.major_id = m.major_id
            LEFT JOIN MajorStats ms ON m.major_id = ms.major_id
            WHERE sc.user_id = %s
            GROUP BY sc.major_id, m.major_name, sc.saved_at
            ORDER BY sc.saved_at DESC
        """, (user_id,))
        
        saved_comparisons = cursor.fetchall()
        
        return jsonify({
            "user_id": user_id,
            "saved_comparisons": saved_comparisons,
            "count": len(saved_comparisons)
        })
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/major-jobs/<int:major_id>', methods=['GET'])
def get_major_jobs(major_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all individual job entries for a specific major
        cursor.execute("""
            SELECT 
                ms.stat_id,
                ms.avg_salary,
                ms.job_growth_rate,
                ms.grad_count,
                ms.year,
                ds.name as source_name,
                ds.url as source_url
            FROM MajorStats ms
            LEFT JOIN DataSource ds ON ms.source_id = ds.source_id
            WHERE ms.major_id = %s
            ORDER BY ms.avg_salary DESC
        """, (major_id,))
        
        jobs = cursor.fetchall()
        
        # Get major name
        cursor.execute("SELECT major_name FROM Major WHERE major_id = %s", (major_id,))
        major_result = cursor.fetchone()
        major_name = major_result['major_name'] if major_result else "Unknown Major"
        
        return jsonify({
            "major_id": major_id,
            "major_name": major_name,
            "jobs": jobs,
            "count": len(jobs)
        })
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/saved-comparisons/<int:user_id>/<int:major_id>', methods=['DELETE'])
def remove_saved_comparison(user_id, major_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM SavedComparison WHERE user_id = %s AND major_id = %s",
            (user_id, major_id)
        )
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Saved comparison not found"}), 404
        
        conn.commit()
        return jsonify({"message": "Saved comparison removed successfully"})
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()





if __name__ == '__main__':
    app.run(debug=True)
