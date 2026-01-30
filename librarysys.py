from enum import unique
from pydoc import synopsis
from flask import Flask, request, render_template, url_for, flash,redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from datetime import timedelta
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from webforms import BorrowForm, BorrowerForm, SearchForm, BookForm, UserForm, LoginForm, EditBorrowerForm, RatingForm, SuggestionForm, FinePaymentForm, ChatForm
from flask_migrate import Migrate
import uuid as uuid
from sqlalchemy import update, func, desc
from sqlalchemy import ForeignKey
import requests
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234567890@localhost/library' #Configuration for connecting to database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) #Creates instance of SQLAlchemy
migrate = Migrate(app, db)
app.config['SECRET_KEY'] = "asgkuaghpuiweghowiuhglauhgpagksudhgiwuerhwlagwes" #Security

# Groq API Configuration for Chatbot
GROQ_API_KEY = "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"  # Replace with your actual Groq API key
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Fine Configuration
FINE_RATE_PER_DAY = 1.00  # $1 per day overdue
FINE_GRACE_PERIOD = 3     # 3 days grace period
MAX_FINE = 50.00          # Maximum fine cap

#Login, Authentication and Registeration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):  
    return Users.query.get(int(user_id)) or Reader.query.get(int(user_id))


def verify_password_hash(stored_hash, password):
    """Verify password against stored hash with fallback for legacy 'sha256' format.

    Tries Werkzeug's `check_password_hash` first. If it raises a ValueError due to
    an unsupported method (for example legacy 'sha256$salt$hash'), this will
    attempt to verify the legacy format by computing sha256(salt + password).
    """
    try:
        return check_password_hash(stored_hash, password)
    except ValueError as e:
        # Fallback for legacy format like 'sha256$salt$hexdigest'
        try:
            parts = stored_hash.split('$')
            if len(parts) == 3 and parts[0] == 'sha256':
                _, salt, hashval = parts
                computed = hashlib.sha256((salt + password).encode()).hexdigest()
                return computed == hashval
        except Exception:
            pass
        # re-raise original error if we cannot handle it
        raise


#Searching
@app.context_processor
def base():
    form = SearchForm() 
    return dict(form=form)

#Models

#Reader Model
class Reader (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    late_returns = db.Column(db.Integer, nullable = False, default=0)
    superuser = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.String(255), nullable=False)
    total_fines_owed = db.Column(db.Float, nullable=False, default=0.0)  # NEW: Track total fines
    #Backref
    borrow = db.relationship('Borrow', backref='borrower')
    ratings = db.relationship('Rating', backref='reader')  # NEW: Reader's ratings
    suggestions = db.relationship('Suggestion', backref='reader')  # NEW: Reader's suggestions


#Book Model
class Book (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    synopsis = db.Column(db.Text, nullable=True)
    available = db.Column(db.Boolean, nullable=False, default=True)
    category = db.Column(db.String(100), nullable=True)  # NEW: Book category
    total_borrows = db.Column(db.Integer, nullable=False, default=0)  # NEW: Track popularity
    #Backref
    borrow = db.relationship('Borrow', backref='book')
    ratings = db.relationship('Rating', backref='book')  # NEW: Book's ratings


#User Model
class  Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    superuser = db.Column(db.Boolean, nullable=False, default=True)
    password_hash = db.Column(db.String(255), nullable=False)

    @property
    def password(self):
      raise AttributeError('password is unreadable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return verify_password_hash(self.password_hash, password)


#Borrow Model
class Borrow (db.Model):
     id = db.Column(db.Integer, primary_key=True)
     borrow_date = db.Column(db.Date, default=date.today())
     book_id = db.Column(db.Integer, ForeignKey(Book.id))
     borrower_id = db.Column (db.Integer, ForeignKey(Reader.id))
     overdue = db.Column(db.Boolean, nullable = False, default=False)
     return_date = db.Column(db.Date, nullable=False, default=date.today() + timedelta(days=20))
     returned = db.Column(db.Boolean, nullable=True, default=False)
     fine_amount = db.Column(db.Float, nullable=False, default=0.0)  # NEW: Fine for this borrow
     fine_paid = db.Column(db.Boolean, nullable=False, default=False)  # NEW: Fine payment status


# ============== NEW MODELS FOR ADDITIONAL FEATURES ==============

#Rating Model - For book feedback and ratings
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, ForeignKey(Book.id), nullable=False)
    reader_id = db.Column(db.Integer, ForeignKey(Reader.id), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    date_posted = db.Column(db.Date, default=date.today())


#Suggestion Model - For book suggestions by readers
class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reader_id = db.Column(db.Integer, ForeignKey(Reader.id), nullable=False)
    suggested_title = db.Column(db.String(255), nullable=False)
    suggested_author = db.Column(db.String(255), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, approved, rejected
    date_suggested = db.Column(db.Date, default=date.today())
    librarian_notes = db.Column(db.Text, nullable=True)


# ============== HELPER FUNCTIONS ==============

def calculate_fine(borrow):
    """Calculate fine for an overdue book"""
    if borrow.returned or not borrow.overdue:
        return 0.0
    
    days_overdue = (date.today() - borrow.return_date).days
    
    if days_overdue <= FINE_GRACE_PERIOD:
        return 0.0
    
    fine = (days_overdue - FINE_GRACE_PERIOD) * FINE_RATE_PER_DAY
    return min(fine, MAX_FINE)  # Apply maximum cap


def get_book_average_rating(book_id):
    """Get average rating for a book"""
    ratings = Rating.query.filter_by(book_id=book_id).all()
    if not ratings:
        return 0
    return sum(r.rating for r in ratings) / len(ratings)


def get_chatbot_response(user_message, context=""):
    """Get response from Groq LLM API with database context"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Gather database context for the chatbot (READ-ONLY)
    db_context = get_library_context()
    
    system_prompt = f"""You are a helpful library assistant chatbot with access to real library data.

LIBRARY DATABASE INFO:
{db_context}

LIBRARY POLICIES:
• Borrowing period: 20 days
• Grace period: 3 days (no fine)
• Fine rate: $1 per day after grace period
• Maximum fine: $50 per book

RESPONSE FORMAT RULES:
• Use bullet points (•) for lists
• Keep responses concise and organized
• Use line breaks between sections
• Bold important information with **text**
• Never write long paragraphs
• Structure information clearly

You help users with:
• Finding books and recommendations
• Checking book availability
• Understanding library policies
• Answering questions about fines and borrowing
• Providing library statistics"""
    
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"I'm sorry, I'm having trouble connecting right now. Please try again later or contact the librarian directly."


def get_library_context():
    """Get current library data for chatbot context (READ-ONLY)"""
    try:
        # Get statistics
        total_books = Book.query.count()
        available_books = Book.query.filter_by(available=True).count()
        total_readers = Reader.query.count()
        active_borrows = Borrow.query.filter_by(returned=False).count()
        overdue_count = Borrow.query.filter_by(overdue=True, returned=False).count()
        
        # Get available books list (limit to 20)
        available_book_list = Book.query.filter_by(available=True).limit(20).all()
        available_titles = [f"• {b.title} by {b.author}" for b in available_book_list]
        
        # Get popular books
        popular_books = db.session.query(
            Book.title, Book.author, func.count(Borrow.id).label('count')
        ).join(Borrow).group_by(Book.id).order_by(desc('count')).limit(5).all()
        popular_list = [f"• {b.title} by {b.author} ({b.count} borrows)" for b in popular_books]
        
        # Get overdue books info
        overdue_borrows = Borrow.query.filter_by(overdue=True, returned=False).limit(10).all()
        overdue_list = [f"• {b.book.title} - borrowed by Reader ID {b.borrower_id}" for b in overdue_borrows if b.book]
        
        context = f"""
CURRENT STATISTICS:
• Total books: {total_books}
• Available books: {available_books}
• Borrowed books: {total_books - available_books}
• Total readers: {total_readers}
• Active borrows: {active_borrows}
• Overdue books: {overdue_count}

AVAILABLE BOOKS (sample):
{chr(10).join(available_titles) if available_titles else '• No books currently available'}

POPULAR BOOKS:
{chr(10).join(popular_list) if popular_list else '• No borrow data yet'}

OVERDUE BOOKS:
{chr(10).join(overdue_list) if overdue_list else '• No overdue books'}
"""
        return context
    except Exception as e:
        return "Database context unavailable." 


#Login choice page
@app.route('/', methods=['GET', 'POST'])
def loginchoice(): 
    return render_template('loginchoicepage.html')

#Reader login page
@app.route('/readerlogin', methods=['GET', 'POST'])
def readerlogin():
    form = LoginForm()
    if form.validate_on_submit():
        reader = Reader.query.filter_by(email=form.email.data).first()
        if reader:
            #check hash
            if verify_password_hash(reader.password_hash, form.password.data):
                login_user(reader)
                return redirect(url_for('readerbookview'))
            else:
                flash("WRONG PASSWORD TRY AGAIN") 
        else:
            flash("USER DOES NOT EXIST")

    return render_template('readerlogin.html', form=form)


#Reader registeration
@app.route('/register', methods=['GET', "POST"])
def borroweradd():
    form = BorrowerForm()
    if form.validate_on_submit():
        reader = Reader.query.filter_by(email=form.email.data).first()
        if reader is None:
            if form.password_hash.data == form.verify_password_hash.data:
                hashed_pw = generate_password_hash(form.password_hash.data)
                reader = Reader(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data,password_hash=hashed_pw)
            
                form.first_name.data = ''
                form.last_name.data = ''
                form.email.data = ''
                form.password_hash.data = ''

                #Add Reader data to database
                db.session.add(reader)
                db.session.commit()
            else:
                flash("Passwords do not match")
                return redirect(url_for('borroweradd'))

        flash("You have been registered successfully")
        return redirect(url_for('loginchoice'))
    #else:
        #flash("Please enter valid information")


    return render_template("registeration.html", form=form)


#Librarian Login page
@app.route('/librarianlogin', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            #check hash
            if verify_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for('bookview'))
            else:
                flash("WRONG PASSWORD TRY AGAIN") 
        else:
            flash("USER DOES NOT EXIST")

    return render_template('librarianlogin.html', form=form)

#Adding User
@app.route('/adduser', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    #Hashing Password
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data)
            user = Users(email=form.email.data, name=form.name.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
    
    return render_template ( "adduser.html", form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for('loginchoice'))

#Books

#Add book
@app.route('/bookadd', methods=['GET', "POST"])
@login_required
def add_book():
    form = BookForm()

    if form.validate_on_submit():
        book = Book(title=form.title.data, author=form.author.data, synopsis=form.synopsis.data, available=True) #Create book object
        #Clear the form
        form.title.data = ''
        form.author.data = ''
        form.synopsis.data = ''


        #Add book data to database
        db.session.add(book)
        db.session.commit()

        flash("Book added to database successfully") #Flash message

    return render_template("bookadd.html", form=form) #Showing web pages

#List of books
@app.route('/books', methods=['GET', 'POST'])
@login_required
def bookview(): 
    books = Book.query.order_by(Book.id) #Grab all books from database and puts them in a list named books
    return render_template('bookview.html', books = books) #Passes the list books into html template  

#View book details for librarian 
@app.route('/books/<int:id>')
@login_required
def viewbook(id):
    book = Book.query.get_or_404(id)
    return render_template('book.html', book=book)

#View book details for reader
@app.route('/readerbooks/<int:id>')
@login_required
def readerbook(id):
    book = Book.query.get_or_404(id)
    return render_template('readerbook.html', book=book)

#Edit book details
@app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    form = BookForm()
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.synopsis = form.synopsis.data

        db.session.add(book)
        db.session.commit()
        flash("Book information has been updated")
        return redirect(url_for('bookview'))
    form.title.data = book.title
    form.author.data = book.author
    form.synopsis.data = book.synopsis
    return render_template('edit_book.html', form=form, id=id)

#Delete book   
@app.route('/books/delete/<int:id>')
@login_required
def delete_book(id):
    book_to_delete = Book.query.get_or_404(id)

    try:
        db.session.delete(book_to_delete)
        db.session.commit()

        flash("Book was deleted from database ")

        books = Book.query.order_by(Book.id)
        return render_template('bookview.html', books = books)

    except:
        flash("Error deleting book")

#Search for books
@app.route('/booksearch', methods=["POST"])
@login_required
def booksearch():
    form = SearchForm()
    books = Book.query

    if form.validate_on_submit(): #If user is librarian 
        
        viewbook.searched = form.searched.data

        books = books.filter(Book.title.like('%' + viewbook.searched + '%'))
        books = books.order_by(Book.title).all()
     
        return render_template("booksearch.html", form=form, searched = viewbook.searched, books = books)

@app.route('/readerbooksearch', methods=["POST"])
@login_required
def readerbooksearch():
    form = SearchForm()
    books = Book.query

    if form.validate_on_submit(): #If user is librarian 
        
        viewbook.searched = form.searched.data

        books = books.filter(Book.title.like('%' + viewbook.searched + '%'))
        books = books.order_by(Book.title).all()
     
        return render_template("readerbooksearch.html", form=form, searched = viewbook.searched, books = books)


#Reader book view
@app.route('/readerbookview', methods=['GET', 'POST'])
@login_required
def readerbookview():
        
    books = Book.query.order_by(Book.id) #Grab all books from database
    return render_template('readerbookview.html', books = books)

#Readers

#View list of Readers
@app.route('/readerview', methods=['GET', 'POST'])
@login_required
def readerview():
    
    readers = Reader.query.order_by(Reader.id) #Grab all readers from database
    return render_template('readerview.html', readers = readers)

#Edit reader details
@app.route('/borrowerview/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_borrower(id):
    reader = Reader.query.get_or_404(id)
    form = EditBorrowerForm()
    if form.validate_on_submit():
        reader.first_name = form.first_name.data
        reader.last_name = form.last_name.data
        reader.email = form.email.data
        

        db.session.add(reader)
        db.session.commit()
        flash("Reader information has been updated")
        print ("we changed something")
        return redirect(url_for('readerview'))
    else :
        print ("there was an issue")
    form.first_name.data = reader.first_name
    form.last_name.data = reader.last_name
    form.email.data = reader.email
    return render_template('edit_borrower.html', form=form, id=id)

#View reader details
@app.route('/readerview/<int:id>', methods=['GET', 'POST'])
@login_required
def borrowerlook(id):
    reader = Reader.query.get_or_404(id)
    return render_template('individualreaderview.html', reader=reader)

#Delete Reader from database
@app.route('/readerview/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def borrowerdelete(id):
    reader_to_delete = Reader.query.get_or_404(id)

    try:
        db.session.delete(reader_to_delete)
        db.session.commit()

        flash("Reader was deleted from database ")

        readers = Reader.query.order_by(Reader.id)
        return render_template('readerview.html', readers = readers)

    except:
        flash("Error deleting reader")

#View your borrows
@app.route('/myborrows')
@login_required
def myborrows():

    print(current_user.superuser)
    #reader = current_user.id
    myborrows = Borrow.query.filter(Borrow.borrower_id == current_user.id).all()
    return render_template('myborrows.html', myborrows = myborrows, current_user = current_user.id)


#Borrows

#Create a borrow
@app.route('/borrowadd', methods=['GET','POST'])
@login_required
def borrowadd():
    form = BorrowForm()

    print(current_user.superuser)

    if form.validate_on_submit():
        
        if  db.session.query(Book.id).filter_by(id = form.book_id.data).first() is not None and db.session.query(Reader.id).filter_by(id = form.borrower_id.data).first() is not None:
            
            book_in_borrow = Book.query.filter_by(id = form.book_id.data).first()
            if book_in_borrow.available != False:      
                borrow = Borrow(book_id=form.book_id.data, borrower_id=form.borrower_id.data)
                #Clear the form  
                update(Book).where(Book.id == form.book_id.data).values(available=False)
                book_in_borrow.available = False
                form.book_id.data = ''
                form.borrower_id.data = '' 
               
                db.session.add(borrow)
                db.session.commit() 
                flash("Borrow added to database successfully")

            else:
                flash("Book is not available")

        else:
            flash("Please enter valid IDs")

    return render_template("borrowadd.html", form=form)

#Return a book 
@app.route('/borrowview/return/<int:id>', methods=['GET','POST'])
@login_required
def returnbook(id):
    borrow_to_confirm = Borrow.query.get_or_404(id)
    borrowed_book = Book.query.filter_by(id = borrow_to_confirm.book_id).first()
    borrower_in_borrow = Reader.query.filter_by(id = borrow_to_confirm.borrower_id).first()

    try:
        if borrow_to_confirm.overdue == False:
            borrowed_book.available = True
            borrow_to_confirm.returned = True

            db.session.commit()

            flash("Return Successful")

            todays_date = date.today()
            borrows = Borrow.query.order_by(Borrow.id)
            for borrow in borrows:
                if (todays_date - borrow.return_date).days > 1:
                    borrow.overdue = True

            return render_template('borrowview.html', borrows = borrows, todays_date=todays_date)

        else:
            borrowed_book.available = True
            borrower_in_borrow.late_returns += 1
            borrow_to_confirm.returned = True

            db.session.commit()

            flash("Return Successful, Late returns updated")

            todays_date = date.today()
            borrows = Borrow.query.order_by(Borrow.id)
            for borrow in borrows:
                if (todays_date - borrow.return_date).days > 1 and not borrow.returned:
                    borrow.overdue = True

            return render_template('borrowview.html', borrows = borrows, todays_date=todays_date)

    except:

        flash("An error occured")

#View list of borrows
@app.route('/borrowview', methods=['GET','POST'])
@login_required
def borrowview():   
    #Grab all borrows from database
    todays_date = date.today()
    borrows = Borrow.query.order_by(Borrow.id)
    for borrow in borrows:
        if (todays_date - borrow.return_date).days > 1:
            borrow.overdue = True

    return render_template('borrowview.html', borrows = borrows, todays_date=todays_date)

@app.route('/borrowhistory')
def borrowhistory():
    todays_date = date.today()
    borrows = Borrow.query.order_by(Borrow.id)
    for borrow in borrows:
        if (todays_date - borrow.return_date).days > 1:
            borrow.overdue = True

    return render_template('allborrows.html', borrows = borrows, todays_date=todays_date)


#Error Handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# ============== ANALYTICS DASHBOARD ==============

@app.route('/dashboard')
@login_required
def dashboard():
    """Analytics Dashboard for Librarians"""
    # Basic Statistics
    total_books = Book.query.count()
    available_books = Book.query.filter_by(available=True).count()
    total_readers = Reader.query.count()
    active_borrows = Borrow.query.filter_by(returned=False).count()
    overdue_count = Borrow.query.filter_by(overdue=True, returned=False).count()
    total_borrows = Borrow.query.count()
    
    # Total fines owed
    total_fines = db.session.query(func.sum(Reader.total_fines_owed)).scalar() or 0
    
    # Most borrowed books (Top 5)
    most_borrowed = db.session.query(
        Book.id, Book.title, Book.author,
        func.count(Borrow.id).label('borrow_count')
    ).join(Borrow).group_by(Book.id).order_by(
        desc('borrow_count')
    ).limit(5).all()
    
    # Most active readers (Top 5)
    most_active_readers = db.session.query(
        Reader.id, Reader.first_name, Reader.last_name,
        func.count(Borrow.id).label('total_borrows')
    ).join(Borrow).group_by(Reader.id).order_by(
        desc('total_borrows')
    ).limit(5).all()
    
    # Recent suggestions
    recent_suggestions = Suggestion.query.filter_by(status='pending').order_by(
        desc(Suggestion.date_suggested)
    ).limit(5).all()
    
    # Top rated books
    top_rated = db.session.query(
        Book.id, Book.title, Book.author,
        func.avg(Rating.rating).label('avg_rating'),
        func.count(Rating.id).label('review_count')
    ).join(Rating).group_by(Book.id).order_by(
        desc('avg_rating')
    ).limit(5).all()
    
    # Monthly borrow stats (last 6 months)
    monthly_stats = []
    for i in range(5, -1, -1):
        month_start = date.today().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        count = Borrow.query.filter(
            Borrow.borrow_date >= month_start,
            Borrow.borrow_date <= month_end
        ).count()
        monthly_stats.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    return render_template('dashboard.html',
        total_books=total_books,
        available_books=available_books,
        total_readers=total_readers,
        active_borrows=active_borrows,
        overdue_count=overdue_count,
        total_borrows=total_borrows,
        total_fines=total_fines,
        most_borrowed=most_borrowed,
        most_active_readers=most_active_readers,
        recent_suggestions=recent_suggestions,
        top_rated=top_rated,
        monthly_stats=monthly_stats
    )


# ============== FINE CALCULATOR ROUTES ==============

@app.route('/fines')
@login_required
def view_fines():
    """View all fines (Librarian view)"""
    # Update all fines first
    borrows = Borrow.query.filter_by(returned=False, overdue=True).all()
    for borrow in borrows:
        borrow.fine_amount = calculate_fine(borrow)
        # Update reader's total fines
        if borrow.borrower:
            borrow.borrower.total_fines_owed = sum(
                b.fine_amount for b in borrow.borrower.borrow 
                if not b.fine_paid and b.fine_amount > 0
            )
    db.session.commit()
    
    # Get all borrows with fines
    fines = Borrow.query.filter(Borrow.fine_amount > 0).order_by(desc(Borrow.fine_amount)).all()
    return render_template('fines.html', fines=fines)


@app.route('/fines/pay/<int:id>', methods=['POST'])
@login_required
def pay_fine(id):
    """Mark a fine as paid"""
    borrow = Borrow.query.get_or_404(id)
    borrow.fine_paid = True
    
    # Update reader's total fines
    if borrow.borrower:
        borrow.borrower.total_fines_owed = sum(
            b.fine_amount for b in borrow.borrower.borrow 
            if not b.fine_paid and b.fine_amount > 0
        )
    
    db.session.commit()
    flash(f"Fine of ${borrow.fine_amount:.2f} marked as paid!")
    return redirect(url_for('view_fines'))


@app.route('/myfines')
@login_required
def my_fines():
    """View reader's own fines"""
    # Update fines first
    borrows = Borrow.query.filter_by(borrower_id=current_user.id, returned=False).all()
    for borrow in borrows:
        if borrow.overdue:
            borrow.fine_amount = calculate_fine(borrow)
    db.session.commit()
    
    my_fines = Borrow.query.filter(
        Borrow.borrower_id == current_user.id,
        Borrow.fine_amount > 0
    ).all()
    
    total_owed = sum(f.fine_amount for f in my_fines if not f.fine_paid)
    return render_template('myfines.html', fines=my_fines, total_owed=total_owed)


# ============== FEEDBACK AND RATING ROUTES ==============

@app.route('/book/<int:id>/rate', methods=['GET', 'POST'])
@login_required
def rate_book(id):
    """Rate and review a book"""
    book = Book.query.get_or_404(id)
    form = RatingForm()
    
    # Check if user has already rated this book
    existing_rating = Rating.query.filter_by(book_id=id, reader_id=current_user.id).first()
    
    if form.validate_on_submit():
        if existing_rating:
            # Update existing rating
            existing_rating.rating = int(form.rating.data)
            existing_rating.review = form.review.data
            existing_rating.date_posted = date.today()
            flash("Your review has been updated!")
        else:
            # Create new rating
            rating = Rating(
                book_id=id,
                reader_id=current_user.id,
                rating=int(form.rating.data),
                review=form.review.data
            )
            db.session.add(rating)
            flash("Thank you for your review!")
        
        db.session.commit()
        return redirect(url_for('book_reviews', id=id))
    
    # Pre-fill form if editing
    if existing_rating:
        form.rating.data = str(existing_rating.rating)
        form.review.data = existing_rating.review
    
    return render_template('rate_book.html', form=form, book=book, existing=existing_rating)


@app.route('/book/<int:id>/reviews')
def book_reviews(id):
    """View all reviews for a book"""
    book = Book.query.get_or_404(id)
    reviews = Rating.query.filter_by(book_id=id).order_by(desc(Rating.date_posted)).all()
    avg_rating = get_book_average_rating(id)
    return render_template('book_reviews.html', book=book, reviews=reviews, avg_rating=avg_rating)


@app.route('/allreviews')
@login_required
def all_reviews():
    """View all reviews (Librarian view)"""
    reviews = Rating.query.order_by(desc(Rating.date_posted)).all()
    return render_template('all_reviews.html', reviews=reviews)


# ============== BOOK SUGGESTION ROUTES ==============

@app.route('/suggest', methods=['GET', 'POST'])
@login_required
def suggest_book():
    """Reader suggests a new book"""
    form = SuggestionForm()
    
    if form.validate_on_submit():
        suggestion = Suggestion(
            reader_id=current_user.id,
            suggested_title=form.suggested_title.data,
            suggested_author=form.suggested_author.data,
            reason=form.reason.data
        )
        db.session.add(suggestion)
        db.session.commit()
        flash("Thank you! Your book suggestion has been submitted.")
        return redirect(url_for('my_suggestions'))
    
    return render_template('suggest_book.html', form=form)


@app.route('/mysuggestions')
@login_required
def my_suggestions():
    """View reader's own suggestions"""
    suggestions = Suggestion.query.filter_by(reader_id=current_user.id).order_by(
        desc(Suggestion.date_suggested)
    ).all()
    return render_template('my_suggestions.html', suggestions=suggestions)


@app.route('/suggestions')
@login_required
def view_suggestions():
    """View all suggestions (Librarian view)"""
    suggestions = Suggestion.query.order_by(desc(Suggestion.date_suggested)).all()
    return render_template('suggestions.html', suggestions=suggestions)


@app.route('/suggestions/<int:id>/approve', methods=['POST'])
@login_required
def approve_suggestion(id):
    """Approve a book suggestion"""
    suggestion = Suggestion.query.get_or_404(id)
    suggestion.status = 'approved'
    db.session.commit()
    flash(f"Suggestion '{suggestion.suggested_title}' has been approved!")
    return redirect(url_for('view_suggestions'))


@app.route('/suggestions/<int:id>/reject', methods=['POST'])
@login_required
def reject_suggestion(id):
    """Reject a book suggestion"""
    suggestion = Suggestion.query.get_or_404(id)
    suggestion.status = 'rejected'
    db.session.commit()
    flash(f"Suggestion '{suggestion.suggested_title}' has been rejected.")
    return redirect(url_for('view_suggestions'))


# ============== CHATBOT ROUTES ==============

@app.route('/chatbot')
@login_required
def chatbot():
    """Chatbot help page (Librarian only)"""
    if not current_user.superuser:
        flash('Access denied. Librarians only.', 'danger')
        return redirect(url_for('readerview'))
    return render_template('chatbot.html')


@app.route('/chatbot/send', methods=['POST'])
@login_required
def chatbot_send():
    """Handle chatbot messages via AJAX (Librarian only)"""
    if not current_user.superuser:
        return jsonify({'response': 'Access denied.'}), 403
    
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Please enter a message.'})
    
    # Get response from Groq API
    bot_response = get_chatbot_response(user_message)
    
    return jsonify({'response': bot_response})


@app.route('/reader/chatbot')
@login_required
def reader_chatbot():
    """Chatbot for readers"""
    if current_user.superuser:
        flash('Please use the librarian chatbot.', 'info')
        return redirect(url_for('chatbot'))
    return render_template('reader_chatbot.html')


@app.route('/reader/chatbot/send', methods=['POST'])
@login_required
def reader_chatbot_send():
    """Handle reader chatbot messages via AJAX"""
    if current_user.superuser:
        return jsonify({'response': 'Please use the librarian chatbot.'}), 403
    
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Please enter a message.'})
    
    # Get response from Groq API
    bot_response = get_chatbot_response(user_message)
    
    return jsonify({'response': bot_response})












