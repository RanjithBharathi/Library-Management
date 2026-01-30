from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, EmailField, IntegerField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Email, Optional, Length
from wtforms.widgets import TextArea

#Form for adding new borrow
class BorrowForm(FlaskForm):
    book_id = IntegerField("book id", validators=[DataRequired(), NumberRange(min=1, max=100)])
    borrower_id = IntegerField("borrower id", validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField("Submit")

#Form for adding borrower
class BorrowerForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email("Enter a valid email address")], widget=TextArea())
    late_returns = IntegerField("Late Returns")
    password_hash = PasswordField("Password", validators=[DataRequired()])
    verify_password_hash = PasswordField("Re-enter Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Form for editing borrower details
class EditBorrowerForm(FlaskForm):
    first_name = StringField("First Name",validators=[DataRequired()])
    last_name = StringField("Last Name",validators=[DataRequired()])
    email = EmailField("Email",validators=[DataRequired()])
    late_returns = IntegerField("Late Returns",validators=[Optional()])
    submit = SubmitField("Submit")

#Form to search books or borrowers
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Form to add book
class BookForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    synopsis = StringField("Synopsis", validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("Submit")

#Form to add user
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email("Enter a valid email address")], widget=TextArea() )
    password_hash = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

#Form used for login
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email("Enter a valid email address")])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

#Form for choice of login
class LoginChoiceForm(FlaskForm):
    librarian_login = SubmitField("Librarian Login")
    borrower_login = SubmitField("Reader Login") 

# ============== NEW FORMS FOR ADDITIONAL FEATURES ==============

#Form for Book Rating and Review
class RatingForm(FlaskForm):
    rating = SelectField("Rating", choices=[('5', '⭐⭐⭐⭐⭐ Excellent'), ('4', '⭐⭐⭐⭐ Very Good'), ('3', '⭐⭐⭐ Good'), ('2', '⭐⭐ Fair'), ('1', '⭐ Poor')], validators=[DataRequired()])
    review = TextAreaField("Your Review", validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField("Submit Review")

#Form for Book Suggestion
class SuggestionForm(FlaskForm):
    suggested_title = StringField("Book Title", validators=[DataRequired(), Length(max=255)])
    suggested_author = StringField("Author Name", validators=[DataRequired(), Length(max=255)])
    reason = TextAreaField("Why should we add this book?", validators=[DataRequired(), Length(min=20, max=500)])
    submit = SubmitField("Submit Suggestion")

#Form for Fine Payment
class FinePaymentForm(FlaskForm):
    amount = HiddenField("Amount")
    submit = SubmitField("Mark as Paid")

#Form for Chatbot
class ChatForm(FlaskForm):
    message = StringField("Message", validators=[DataRequired(), Length(max=500)])
    submit = SubmitField("Send")
