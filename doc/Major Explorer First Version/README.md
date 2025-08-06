# College Major Explorer

A web application for exploring and comparing college majors based on salary, job growth, and personal interests.

## Features

### 🔐 Authentication System
- **User Registration**: Create new accounts with username, email, and secure password
- **User Login**: Login with username or email
- **Password Security**: Passwords are hashed using bcrypt
- **Form Validation**: Real-time validation for email format and password strength
- **Session Management**: Secure user sessions

### 📊 Major Exploration
- **Interactive Charts**: Bubble chart visualization of majors
- **Filtering**: Filter by interest area, minimum salary, and job growth rate
- **Comparison**: Save and compare different majors
- **Data Visualization**: Chart.js powered interactive graphs

### 💼 Job Submissions
- **Personal Job Tracking**: Submit and track your own job experiences
- **CRUD Operations**: Create, read, update, and delete job submissions
- **Interest Area Mapping**: Link jobs to specific interest areas

## Setup Instructions

### Prerequisites
- Python 3.7+
- MySQL/MariaDB database
- Web browser

### Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**:
   - Create a MySQL database named `college_major_db`
   - Run the SQL script to create the Users table:
   ```sql
   source setup_users_table.sql;
   ```

4. **Configure environment variables** (optional):
   Create a `.env` file in the project root:
   ```
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_NAME=college_major_db
   DB_PORT=3306
   ```

5. **Start the Flask server**:
   ```bash
   python "app (1).py"
   ```

6. **Open the application**:
   - Open `cs411projectfrontend.html` in your web browser
   - Or serve it through a local web server

## Usage

### Creating an Account
1. Click "Don't have an account? Sign up" on the login form
2. Fill in your username, email, and password
3. The password must be at least 8 characters with uppercase, lowercase, and digit
4. Click "Sign Up" to create your account

### Logging In
1. Enter your username or email
2. Enter your password
3. Click "Login"

### Exploring Majors
1. Select an interest area from the dropdown
2. Adjust minimum salary and growth rate sliders
3. Click "Apply Filters" to see matching majors
4. Click on bubbles to see detailed information
5. Use "Save Comparison" to save interesting majors

### Managing Job Submissions
1. After logging in, scroll down to "My Job Submissions"
2. Fill out the job submission form with your experience
3. View, edit, or delete your submissions as needed

## API Endpoints

### Authentication
- `POST /signup` - Register a new user
- `POST /login` - User login
- `GET /user/<user_id>` - Get user profile

### Majors and Data
- `GET /majors` - Get all majors with statistics
- `GET /interest-areas` - Get all interest areas
- `POST /save-comparison` - Save major comparison

### Job Submissions
- `POST /submit-job` - Submit a new job
- `GET /user-submissions/<user_id>` - Get user's job submissions
- `PUT /user-submissions/<submission_id>` - Update a submission
- `DELETE /user-submissions/<submission_id>` - Delete a submission

## Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **Input Validation**: Server-side validation for all inputs
- **Email Format Validation**: Proper email format checking
- **Password Strength Requirements**: Enforced strong password policy
- **SQL Injection Prevention**: Parameterized queries

## File Structure

```
cs411/
├── app (1).py                 # Flask backend server
├── cs411projectfrontend.html  # Frontend application
├── requirements.txt           # Python dependencies
├── setup_users_table.sql     # Database setup script
└── README.md                 # This file
```

## Technologies Used

- **Backend**: Flask, MySQL, bcrypt
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js
- **Styling**: Custom CSS with modern design

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check your MySQL server is running
   - Verify database credentials in `.env` file or default config
   - Ensure the database `college_major_db` exists

2. **Port Already in Use**:
   - Change the port in `app (1).py` or kill the process using port 5000

3. **CORS Errors**:
   - Ensure Flask-CORS is properly installed
   - Check that the frontend is accessing the correct backend URL

4. **Password Hashing Issues**:
   - Make sure bcrypt is installed: `pip install bcrypt`

### Getting Help

If you encounter issues:
1. Check the browser console for JavaScript errors
2. Check the Flask server console for Python errors
3. Verify all dependencies are installed correctly
4. Ensure the database is properly set up

## Future Enhancements

- User profile management
- Password reset functionality
- Email verification
- Advanced filtering options
- Export functionality for comparisons
- Mobile-responsive design improvements 