from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from jinja2.exceptions import TemplateNotFound  # Import TemplateNotFound

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secret key for session management

bcrypt = Bcrypt(app)

# Configure SQLAlchemy for database management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Define Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html')
    except TemplateNotFound:
        return "Error: Template 'register.html' not found"

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                session['user_id'] = user.id  # Store user ID in session
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid username or password'
                return render_template('login.html', error=error)
        return render_template('login.html')
    except TemplateNotFound:
        return "Error: Template 'login.html' not found"

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        if request.method == 'POST':
            title = request.form['title']
            date = request.form['date']
            new_event = Event(title=title, date=date, user_id=user_id)
            db.session.add(new_event)
            db.session.commit()
            return redirect(url_for('dashboard'))
        events = Event.query.filter_by(user_id=user_id).all()
        return render_template('dashboard.html', events=events)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

