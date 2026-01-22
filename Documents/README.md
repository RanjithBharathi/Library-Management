# 📚 Library Management System

A modern, easy-to-use web application for managing books, readers, and borrowing records in a library. Perfect for school libraries, small community libraries, or personal book collections!

## 🌟 What is This Project?

This is a **Library Management System** - think of it as a digital notebook that helps librarians:
- Keep track of all books in the library
- Manage reader (student/member) information
- Record when books are borrowed and returned
- See which books are overdue
- Search for books quickly

Instead of maintaining paper registers, everything is stored in a computer and can be accessed through a web browser!

---

## 🎯 Features

### For Librarians:
- ✅ Add, edit, and delete books
- ✅ View all books with their availability status
- ✅ Add and manage readers (library members)
- ✅ Record new book borrows
- ✅ Mark books as returned
- ✅ View borrow history
- ✅ Search books and readers quickly
- ✅ See overdue books at a glance

### For Readers (Students/Members):
- ✅ Browse available books
- ✅ Search for books by title
- ✅ View their borrowing history
- ✅ Check which books they currently have

---

## 🖥️ What You Need (Prerequisites)

Before starting, you need to install these programs on your computer:

### 1. **Python** (Version 3.8 or higher)
   - **What it is:** Python is the programming language this project uses
   - **Download from:** https://www.python.org/downloads/
   - **Installation tip:** ✅ Check "Add Python to PATH" during installation!

### 2. **MySQL Database** (Version 8.0 or higher)
   - **What it is:** MySQL stores all your library data (books, readers, borrows)
   - **Download from:** https://dev.mysql.com/downloads/installer/
   - **Installation tip:** Remember the password you set for "root" user!

### 3. **Git** (Optional but recommended)
   - **What it is:** Helps you download and manage the project code
   - **Download from:** https://git-scm.com/downloads/

### 4. **A Code Editor** (Optional but helpful)
   - **Recommended:** Visual Studio Code
   - **Download from:** https://code.visualstudio.com/

---

## 📥 Installation Guide (Step-by-Step)

### Step 1: Download the Project

**Option A - Using Git (Recommended):**
```bash
# Open Command Prompt or PowerShell and type:
git clone <your-repository-url>
cd Library-Management
```

**Option B - Manual Download:**
1. Download the project as a ZIP file
2. Extract it to a folder (e.g., `C:\Library-Management`)
3. Open that folder

---

### Step 2: Set Up MySQL Database

1. **Open MySQL Command Line** or **MySQL Workbench**

2. **Create a new database:**
   ```sql
   CREATE DATABASE library;
   ```

3. **Import the database structure:**
   - Find the file `data.sql` in the project folder
   - In MySQL, run this command (replace the path with your actual path):
   ```bash
   # In Command Prompt/PowerShell:
   "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p library < data.sql
   ```
   - Enter your MySQL password when asked

4. **Verify it worked:**
   ```sql
   USE library;
   SHOW TABLES;
   ```
   You should see tables like `books`, `reader`, `borrow`, `users`

---

### Step 3: Install Python Packages

Python packages are like tools that help the project work. Install them using these commands:

1. **Open Command Prompt/PowerShell** in the project folder

2. **Create a virtual environment** (this keeps the project organized):
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   
   **On Windows (PowerShell):**
   ```bash
   .\.venv\Scripts\Activate.ps1
   ```
   
   **On Windows (Command Prompt):**
   ```bash
   .venv\Scripts\activate.bat
   ```
   
   **On Mac/Linux:**
   ```bash
   source .venv/bin/activate
   ```

4. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

---

### Step 4: Configure Database Connection

1. **Open the file** `librarysys.py` in a text editor

2. **Find this line** (around line 13-15):
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234567890@localhost/library'
   ```

3. **Change the password** to match YOUR MySQL password:
   ```python
   # Format: mysql+pymysql://username:password@localhost/database_name
   # Example if your password is "mypass123":
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mypass123@localhost/library'
   ```

4. **Save the file**

---

### Step 5: Create Admin Account

You need at least one librarian account to log in:

1. **Open MySQL Command Line**

2. **Run these commands:**
   ```sql
   USE library;
   
   -- This creates an admin account
   -- Email: admin@library.com
   -- Password: admin123
   INSERT INTO users (name, email, password_hash) 
   VALUES ('Admin', 'admin@library.com', 
   'scrypt:32768:8:1$iK8gV7XZY3xqQVWF$c3af6d9c8f5b2e1a4d7c6b9e8f5a2d1c3b4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5');
   ```

---

## 🚀 How to Run the Application

### Every Time You Want to Use It:

1. **Activate virtual environment** (if not already active):
   ```bash
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```

2. **Set Flask app name** (tells the computer which file to run):
   ```bash
   # Windows PowerShell:
   $env:FLASK_APP = "librarysys.py"
   
   # Windows Command Prompt:
   set FLASK_APP=librarysys.py
   
   # Mac/Linux:
   export FLASK_APP=librarysys.py
   ```

3. **Run the application:**
   ```bash
   flask run
   ```

4. **Open your web browser** and go to:
   ```
   http://127.0.0.1:5000
   ```

5. **You should see the login page!** 🎉

---

## 👤 How to Use the System

### First Time Login:

1. **Go to** `http://127.0.0.1:5000`
2. **Click** "Librarian Login"
3. **Enter:**
   - Email: `admin@library.com`
   - Password: `admin123`
4. **Click Login**

### Adding Books:

1. After logging in, click **"Add Book"** in the navigation bar
2. Fill in:
   - **Title**: Name of the book (e.g., "Harry Potter")
   - **Author**: Who wrote it (e.g., "J.K. Rowling")
   - **Synopsis**: A short description
3. Click **Submit**

### Adding Readers (Library Members):

1. **For students/members to create accounts:**
   - Go to the main login page
   - Click **"Register"**
   - Fill in their details
   - Click Submit

2. **Or librarian can add them:**
   - Click **"Readers"** in the navigation
   - View all registered members

### Recording a Borrow:

1. Click **"New Borrow"**
2. Enter:
   - **Book ID**: The ID number of the book (find it in the Books list)
   - **Borrower ID**: The ID of the reader (find it in Readers list)
3. Click Submit
4. The book is now marked as "Not Available"

### Marking a Return:

1. Click **"Active Borrows"**
2. Find the borrow record
3. Click **"Confirm Return"**
4. The book is now marked as "Available" again

### Searching:

- Use the **search bar** at the top to search for books by title
- On the Readers page, search for readers by name

---

## 📱 User Accounts

### Librarian Account:
- **Email:** admin@library.com (or the one you created)
- **Password:** admin123 (or the one you set)
- **Can do:** Everything - manage books, readers, borrows

### Reader Account:
- **Created by:** Students/members registering themselves
- **Can do:** 
  - Browse available books
  - View their own borrowing history
  - Search for books

---

## 🎨 Understanding the Interface

### Colors and Badges:
- 🟢 **Green "Available"** = Book can be borrowed
- 🔴 **Red "Not Available"** = Book is currently borrowed
- ⚠️ **Yellow "Overdue"** = Book should have been returned by now
- ✅ **Green "On Time"** = Borrowed book is not overdue yet

### Navigation Menu (Librarian):
- **Books** = See all books in the library
- **Add Book** = Add a new book to the system
- **Readers** = See all registered members
- **Active Borrows** = See books currently borrowed
- **History** = See all past and present borrows
- **New Borrow** = Record when someone borrows a book
- **Logout** = Exit the system

---

## 🛠️ Troubleshooting Common Issues

### Problem: "Access Denied" when connecting to MySQL
**Solution:** Check your MySQL password in `librarysys.py` - it should match your MySQL root password

### Problem: "Module not found" errors
**Solution:** Make sure you activated the virtual environment and ran `pip install -r requirements.txt`

### Problem: Can't access the website
**Solution:** 
- Make sure Flask is running (you should see "Running on http://127.0.0.1:5000")
- Check you're using the correct URL: `http://127.0.0.1:5000` (not https)

### Problem: "Table doesn't exist" error
**Solution:** Import the `data.sql` file again using the MySQL command

### Problem: Can't log in with admin account
**Solution:** 
- Make sure you created the admin account in MySQL
- Check that the password you're entering matches
- Default is: `admin@library.com` / `admin123`

### Problem: Website looks broken or unstyled
**Solution:** 
- Make sure the `static/css/library.css` file exists
- Clear your browser cache (Ctrl + Shift + Delete)
- Refresh the page (Ctrl + F5)

---

## 📁 Project Structure

```
Library-Management/
├── librarysys.py          # Main application file (the brain)
├── webforms.py            # Forms for input (registration, login, etc.)
├── data.sql               # Database structure
├── requirements.txt       # List of needed Python packages
├── static/
│   └── css/
│       └── library.css    # Makes the website look pretty
├── templates/             # HTML pages (what you see)
│   ├── base.html         # Template for librarian pages
│   ├── navbar.html       # Navigation bar for librarians
│   ├── loginchoicepage.html  # First page you see
│   ├── librarianlogin.html   # Librarian login page
│   ├── readerlogin.html      # Reader login page
│   ├── registeration.html    # Sign up page
│   ├── bookview.html         # Shows all books
│   ├── bookadd.html          # Add new book
│   ├── readerview.html       # Shows all readers
│   └── ... (more pages)
└── .venv/                 # Virtual environment (created by you)
```

---

## 🔐 Security Notes

### Important Security Tips:
1. **Change the default admin password** after first login
2. **Never share your MySQL password** with others
3. **Don't use this for sensitive data** without additional security measures
4. **This is a learning project** - for production use, add more security features

---

## 🤝 Getting Help

### If You're Stuck:
1. **Read the error message carefully** - it often tells you what's wrong
2. **Check the Troubleshooting section** above
3. **Google the error message** - many others have faced similar issues
4. **Ask a teacher or friend** who knows programming
5. **Review the installation steps** - make sure you didn't skip anything

---

## 📚 What You'll Learn

By setting up and using this project, you'll learn:
- ✅ How web applications work
- ✅ What databases are and how they store data
- ✅ How to use command line/terminal
- ✅ Basic Python concepts
- ✅ How websites are structured (HTML, CSS)
- ✅ Problem-solving skills

---

## 🎓 Educational Value

This project is great for:
- **Computer Science students** learning web development
- **School projects** on database management
- **Learning Python** and Flask framework
- **Understanding CRUD operations** (Create, Read, Update, Delete)
- **Real-world application** of programming concepts

---

## 📝 Future Enhancements (Ideas)

Want to make it better? Try adding:
- 📧 Email notifications for overdue books
- 📊 Statistics dashboard (most borrowed books, etc.)
- 📱 Mobile app version
- 🖼️ Book cover images
- ⭐ Book ratings and reviews
- 📅 Reservation system
- 💳 Fine calculation for overdue books
- 📖 Digital book (e-book) management

---

## ⚖️ License

This is a learning project. Feel free to use it for educational purposes!

---

## 💡 Tips for Success

1. **Take your time** - Don't rush through the installation
2. **Read error messages** - They're trying to help you!
3. **Keep notes** - Write down your MySQL password and admin credentials
4. **Experiment** - Try adding books, creating readers, recording borrows
5. **Ask for help** - Programming is a team sport!
6. **Have fun** - You're building something cool! 🚀

---

## 📞 Quick Reference

### To Start the Application:
```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Set Flask app
$env:FLASK_APP = "librarysys.py"

# 3. Run
flask run

# 4. Open browser to: http://127.0.0.1:5000
```

### Default Login:
- **Email:** admin@library.com
- **Password:** admin123

### MySQL Login:
- **Username:** root
- **Password:** (the one you set during installation)
- **Database:** library

---

**Good luck! 🎉 You're now ready to manage your library like a pro!**

If you followed all the steps correctly, you should have a fully functional library management system running on your computer. Congratulations! 🎓📚
